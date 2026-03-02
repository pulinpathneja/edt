"""Demo seed and reset endpoints for showcasing the app."""
from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_device_id
from app.models.user import DeviceSession, TripDraft, WishlistItem

router = APIRouter()

# Pre-defined wishlist items for demo
_DEMO_WISHLIST = [
    {
        "poi_name": "Colosseum",
        "city": "Rome",
        "country": "Italy",
        "category": "sightseeing",
        "image_url": "https://plus.unsplash.com/premium_photo-1661938399624-3495425e5027?w=400&h=300&fit=crop&auto=format",
        "description": "Iconic Roman amphitheater, skip-the-line entry",
    },
    {
        "poi_name": "Eiffel Tower",
        "city": "Paris",
        "country": "France",
        "category": "sightseeing",
        "image_url": "https://plus.unsplash.com/premium_photo-1661919210043-fd847a58522d?w=400&h=300&fit=crop&auto=format",
        "description": "Iron lattice tower on the Champ de Mars",
    },
    {
        "poi_name": "Fushimi Inari Shrine",
        "city": "Kyoto",
        "country": "Japan",
        "category": "sightseeing",
        "image_url": "https://images.unsplash.com/photo-1693378173709-2197ce8c5af3?w=400&h=300&fit=crop&auto=format",
        "description": "Thousands of vermillion torii gates winding up a mountainside",
    },
    {
        "poi_name": "Sagrada Familia",
        "city": "Barcelona",
        "country": "Spain",
        "category": "sightseeing",
        "image_url": "https://plus.unsplash.com/premium_photo-1661885514351-ad93dcfb25f3?w=400&h=300&fit=crop&auto=format",
        "description": "Gaudí's unfinished basilica masterpiece",
    },
]


@router.post("/seed")
async def seed_demo(
    device_id: str = Depends(require_device_id),
    db: AsyncSession = Depends(get_db),
):
    """Seed demo data: session, active draft, and wishlist items."""
    # 1. Upsert DeviceSession
    result = await db.execute(
        select(DeviceSession).where(DeviceSession.device_id == device_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        session = DeviceSession(device_id=device_id, platform="demo")
        db.add(session)
        await db.commit()

    # 2. Abandon existing active drafts
    result = await db.execute(
        select(TripDraft).where(
            TripDraft.device_id == device_id, TripDraft.status == "active"
        )
    )
    existing_drafts = result.scalars().all()
    for d in existing_drafts:
        d.status = "abandoned"
    await db.commit()

    # 3. Create demo draft
    draft = TripDraft(
        device_id=device_id,
        status="active",
        current_step=2,
        country_id="italy",
        country_name="Italy",
        start_date=date(2026, 3, 20),
        end_date=date(2026, 3, 29),
        group_type="couple",
        group_size=2,
        vibes=["cultural", "romantic", "foodie"],
        budget_level=3,
        pacing="moderate",
    )
    db.add(draft)
    await db.commit()

    # 4. Seed wishlist items (skip duplicates)
    added = 0
    for item_data in _DEMO_WISHLIST:
        existing = await db.execute(
            select(WishlistItem).where(
                WishlistItem.device_id == device_id,
                WishlistItem.poi_name == item_data["poi_name"],
                WishlistItem.city == item_data["city"],
            )
        )
        if existing.scalar_one_or_none() is None:
            item = WishlistItem(device_id=device_id, **item_data)
            db.add(item)
            added += 1

    await db.commit()

    return {
        "status": "seeded",
        "draft_id": str(draft.id),
        "wishlist_items_added": added,
    }


@router.post("/reset")
async def reset_demo(
    device_id: str = Depends(require_device_id),
    db: AsyncSession = Depends(get_db),
):
    """Delete all drafts and wishlist items for this device."""
    await db.execute(
        delete(TripDraft).where(TripDraft.device_id == device_id)
    )
    await db.execute(
        delete(WishlistItem).where(WishlistItem.device_id == device_id)
    )
    await db.commit()
    return {"status": "reset"}
