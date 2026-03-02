from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_device_id
from app.models.user import DeviceSession
from app.schemas.user import SessionRegisterRequest, SessionResponse

router = APIRouter()


@router.post("/register", response_model=SessionResponse)
async def register_session(
    body: SessionRegisterRequest = None,
    device_id: str = Depends(require_device_id),
    db: AsyncSession = Depends(get_db),
):
    """Upsert a device session. Creates on first call, updates last_seen on subsequent calls."""
    if body is None:
        body = SessionRegisterRequest()

    result = await db.execute(
        select(DeviceSession).where(DeviceSession.device_id == device_id)
    )
    session = result.scalar_one_or_none()

    if session:
        session.last_seen_at = datetime.utcnow()
        if body.platform:
            session.platform = body.platform
        if body.app_version:
            session.app_version = body.app_version
    else:
        session = DeviceSession(
            device_id=device_id,
            platform=body.platform,
            app_version=body.app_version,
        )
        db.add(session)

    await db.commit()
    await db.refresh(session)
    return session
