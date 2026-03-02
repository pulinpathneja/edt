from typing import AsyncGenerator
from fastapi import Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def require_device_id(x_device_id: str = Header(...)) -> str:
    """Extract and validate X-Device-ID header."""
    if not x_device_id or len(x_device_id) > 64:
        raise HTTPException(status_code=400, detail="Invalid X-Device-ID header")
    return x_device_id
