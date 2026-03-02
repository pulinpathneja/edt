from pydantic import BaseModel
from typing import Optional, List, Any
from uuid import UUID
from datetime import date, datetime


class DraftCreateRequest(BaseModel):
    current_step: int = 0
    country_id: Optional[str] = None
    country_name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    group_type: Optional[str] = None
    group_size: Optional[int] = None
    vibes: Optional[List[str]] = None
    budget_level: Optional[int] = None
    pacing: Optional[str] = None
    selected_allocation: Optional[Any] = None


class DraftUpdateRequest(BaseModel):
    current_step: Optional[int] = None
    country_id: Optional[str] = None
    country_name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    group_type: Optional[str] = None
    group_size: Optional[int] = None
    vibes: Optional[List[str]] = None
    budget_level: Optional[int] = None
    pacing: Optional[str] = None
    selected_allocation: Optional[Any] = None
    status: Optional[str] = None


class DraftResponse(BaseModel):
    id: UUID
    device_id: str
    status: str
    current_step: int
    country_id: Optional[str] = None
    country_name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    group_type: Optional[str] = None
    group_size: Optional[int] = None
    vibes: Optional[List[str]] = None
    budget_level: Optional[int] = None
    pacing: Optional[str] = None
    selected_allocation: Optional[Any] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
