from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import date, time, datetime
from decimal import Decimal

from app.schemas.poi import POIResponse


class TripRequestCreate(BaseModel):
    """Create a new trip request."""

    user_id: Optional[UUID] = None

    # Basic Info
    destination_city: str = "Rome"
    start_date: date
    end_date: date

    # Persona Selection
    group_type: str  # family, couple, solo, friends, etc.
    group_size: int = 1
    has_kids: bool = False
    kids_ages: Optional[List[int]] = None
    has_seniors: bool = False

    # Preferences
    vibes: List[str]  # selected vibes
    budget_level: int = Field(ge=1, le=5)  # 1-5
    daily_budget: Optional[Decimal] = None
    pacing: str = "moderate"  # slow, moderate, fast

    # Constraints
    mobility_constraints: Optional[List[str]] = None
    dietary_restrictions: Optional[List[str]] = None

    # Weather & Time Preferences
    prefer_outdoor: Optional[bool] = None  # None = no preference
    prefer_indoor: Optional[bool] = None
    avoid_heat: bool = False  # Avoid outdoor activities in peak heat
    early_riser: bool = False  # Prefer early morning activities
    night_owl: bool = False  # Prefer evening/night activities

    @property
    def trip_month(self) -> int:
        """Get the primary month of the trip."""
        return self.start_date.month

    @property
    def trip_season(self) -> str:
        """Derive season from start_date."""
        month = self.start_date.month
        if month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        elif month in [9, 10, 11]:
            return "fall"
        else:
            return "winter"

    @property
    def is_peak_summer(self) -> bool:
        """Check if trip is during peak summer heat."""
        return self.start_date.month in [7, 8]

    @property
    def is_holiday_season(self) -> bool:
        """Check if trip is during major holiday periods."""
        month = self.start_date.month
        day = self.start_date.day
        # Christmas/New Year
        if month == 12 and day >= 20:
            return True
        if month == 1 and day <= 6:
            return True
        # Easter approximate (March-April)
        if month in [3, 4]:
            return True  # Simplified - would need actual Easter calc
        return False


class TripRequestResponse(TripRequestCreate):
    """Response schema for trip request."""

    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class ItineraryItemResponse(BaseModel):
    """Response schema for an itinerary item."""

    id: UUID
    poi_id: Optional[UUID] = None
    sequence_order: int
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    selection_reason: Optional[str] = None
    persona_match_score: Optional[float] = None
    travel_time_from_previous: Optional[int] = None
    travel_mode: Optional[str] = None

    # Include POI details
    poi: Optional[POIResponse] = None

    class Config:
        from_attributes = True


class ItineraryDayResponse(BaseModel):
    """Response schema for an itinerary day."""

    id: UUID
    day_number: int
    date: Optional[date] = None
    theme: Optional[str] = None
    estimated_cost: Optional[Decimal] = None
    pacing_score: Optional[float] = None

    items: List[ItineraryItemResponse] = []

    class Config:
        from_attributes = True


class ItineraryResponse(BaseModel):
    """Response schema for an itinerary."""

    id: UUID
    trip_request_id: UUID
    total_estimated_cost: Optional[Decimal] = None
    generation_method: Optional[str] = None
    created_at: datetime

    days: List[ItineraryDayResponse] = []

    class Config:
        from_attributes = True


class GenerateItineraryRequest(BaseModel):
    """Request to generate an itinerary."""

    trip_request: TripRequestCreate

    # Optional overrides
    must_include_pois: Optional[List[UUID]] = None  # POIs that must be included
    exclude_pois: Optional[List[UUID]] = None  # POIs to exclude
