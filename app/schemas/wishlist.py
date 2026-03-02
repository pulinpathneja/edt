from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class WishlistAddRequest(BaseModel):
    poi_name: str
    city: Optional[str] = None
    country: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    description: Optional[str] = None


class WishlistItemResponse(BaseModel):
    id: UUID
    device_id: str
    poi_name: str
    city: Optional[str] = None
    country: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class WishlistCheckResponse(BaseModel):
    is_wishlisted: bool
    item_id: Optional[UUID] = None
