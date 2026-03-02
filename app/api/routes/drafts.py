from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_device_id
from app.models.user import TripDraft
from app.schemas.draft import DraftCreateRequest, DraftUpdateRequest, DraftResponse

router = APIRouter()


@router.get("/active", response_model=Optional[DraftResponse])
async def get_active_draft(
    device_id: str = Depends(require_device_id),
    db: AsyncSession = Depends(get_db),
):
    """Get the most recent active draft for this device."""
    result = await db.execute(
        select(TripDraft)
        .where(TripDraft.device_id == device_id, TripDraft.status == "active")
        .order_by(TripDraft.updated_at.desc())
        .limit(1)
    )
    draft = result.scalar_one_or_none()
    return draft


@router.post("/", response_model=DraftResponse)
async def create_draft(
    body: DraftCreateRequest,
    device_id: str = Depends(require_device_id),
    db: AsyncSession = Depends(get_db),
):
    """Create a new draft. Auto-abandons any previous active draft."""
    # Abandon previous active drafts
    await db.execute(
        update(TripDraft)
        .where(TripDraft.device_id == device_id, TripDraft.status == "active")
        .values(status="abandoned")
    )

    draft = TripDraft(
        device_id=device_id,
        **body.model_dump(exclude_none=True),
    )
    db.add(draft)
    await db.commit()
    await db.refresh(draft)
    return draft


@router.patch("/{draft_id}", response_model=DraftResponse)
async def update_draft(
    draft_id: UUID,
    body: DraftUpdateRequest,
    device_id: str = Depends(require_device_id),
    db: AsyncSession = Depends(get_db),
):
    """Partial update of a draft (e.g. on wizard step change)."""
    result = await db.execute(
        select(TripDraft).where(
            TripDraft.id == draft_id, TripDraft.device_id == device_id
        )
    )
    draft = result.scalar_one_or_none()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(draft, field, value)

    await db.commit()
    await db.refresh(draft)
    return draft


@router.delete("/{draft_id}")
async def delete_draft(
    draft_id: UUID,
    device_id: str = Depends(require_device_id),
    db: AsyncSession = Depends(get_db),
):
    """Discard a draft."""
    result = await db.execute(
        select(TripDraft).where(
            TripDraft.id == draft_id, TripDraft.device_id == device_id
        )
    )
    draft = result.scalar_one_or_none()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    await db.delete(draft)
    await db.commit()
    return {"status": "deleted", "id": str(draft_id)}
