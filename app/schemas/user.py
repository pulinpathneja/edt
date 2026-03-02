from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class SessionRegisterRequest(BaseModel):
    platform: Optional[str] = None
    app_version: Optional[str] = None


class SessionResponse(BaseModel):
    id: UUID
    device_id: str
    platform: Optional[str] = None
    app_version: Optional[str] = None
    last_seen_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True
