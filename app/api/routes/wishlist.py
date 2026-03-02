from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_device_id
from app.models.user import WishlistItem
from app.schemas.wishlist import WishlistAddRequest, WishlistItemResponse, WishlistCheckResponse

router = APIRouter()


@router.get("/", response_model=List[WishlistItemResponse])
async def list_wishlist(
    device_id: str = Depends(require_device_id),
    db: AsyncSession = Depends(get_db),
):
    """List all wishlist items for this device."""
    result = await db.execute(
        select(WishlistItem)
        .where(WishlistItem.device_id == device_id)
        .order_by(WishlistItem.created_at.desc())
    )
    return result.scalars().all()


@router.post("/", response_model=WishlistItemResponse)
async def add_to_wishlist(
    body: WishlistAddRequest,
    device_id: str = Depends(require_device_id),
    db: AsyncSession = Depends(get_db),
):
    """Add an item to the wishlist. Duplicate check on poi_name + city."""
    # Check for duplicate
    result = await db.execute(
        select(WishlistItem).where(
            and_(
                WishlistItem.device_id == device_id,
                WishlistItem.poi_name == body.poi_name,
                WishlistItem.city == body.city,
            )
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="Item already in wishlist")

    item = WishlistItem(
        device_id=device_id,
        **body.model_dump(),
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{item_id}")
async def remove_from_wishlist(
    item_id: UUID,
    device_id: str = Depends(require_device_id),
    db: AsyncSession = Depends(get_db),
):
    """Remove an item from the wishlist."""
    result = await db.execute(
        select(WishlistItem).where(
            WishlistItem.id == item_id, WishlistItem.device_id == device_id
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Wishlist item not found")

    await db.delete(item)
    await db.commit()
    return {"status": "deleted", "id": str(item_id)}


@router.get("/check", response_model=WishlistCheckResponse)
async def check_wishlisted(
    poi_name: str = Query(...),
    city: str = Query(None),
    device_id: str = Depends(require_device_id),
    db: AsyncSession = Depends(get_db),
):
    """Check if a poi_name + city combination is wishlisted."""
    conditions = [
        WishlistItem.device_id == device_id,
        WishlistItem.poi_name == poi_name,
    ]
    if city:
        conditions.append(WishlistItem.city == city)

    result = await db.execute(
        select(WishlistItem).where(and_(*conditions))
    )
    item = result.scalar_one_or_none()
    return WishlistCheckResponse(
        is_wishlisted=item is not None,
        item_id=item.id if item else None,
    )
