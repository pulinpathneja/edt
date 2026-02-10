from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class POIPersonaScoresCreate(BaseModel):
    """Create persona scores for a POI."""

    # Group Type Scores
    score_family: float = Field(default=0.5, ge=0, le=1)
    score_kids: float = Field(default=0.5, ge=0, le=1)
    score_couple: float = Field(default=0.5, ge=0, le=1)
    score_honeymoon: float = Field(default=0.5, ge=0, le=1)
    score_solo: float = Field(default=0.5, ge=0, le=1)
    score_friends: float = Field(default=0.5, ge=0, le=1)
    score_seniors: float = Field(default=0.5, ge=0, le=1)
    score_business: float = Field(default=0.5, ge=0, le=1)

    # Vibe Scores
    score_adventure: float = Field(default=0.5, ge=0, le=1)
    score_relaxation: float = Field(default=0.5, ge=0, le=1)
    score_cultural: float = Field(default=0.5, ge=0, le=1)
    score_foodie: float = Field(default=0.5, ge=0, le=1)
    score_nightlife: float = Field(default=0.5, ge=0, le=1)
    score_nature: float = Field(default=0.5, ge=0, le=1)
    score_shopping: float = Field(default=0.5, ge=0, le=1)
    score_photography: float = Field(default=0.5, ge=0, le=1)
    score_wellness: float = Field(default=0.5, ge=0, le=1)
    score_romantic: float = Field(default=0.5, ge=0, le=1)

    # Practical Scores
    score_accessibility: float = Field(default=0.5, ge=0, le=1)
    score_indoor: float = Field(default=0.5, ge=0, le=1)


class POIPersonaScoresResponse(POIPersonaScoresCreate):
    """Response schema for persona scores."""

    poi_id: UUID

    class Config:
        from_attributes = True


class POIAttributesCreate(BaseModel):
    """Create attributes for a POI."""

    is_kid_friendly: bool = True
    is_pet_friendly: bool = False
    is_wheelchair_accessible: bool = False
    requires_reservation: bool = False
    requires_advance_booking_days: int = 0

    is_indoor: Optional[bool] = None
    is_outdoor: Optional[bool] = None
    physical_intensity: Optional[int] = Field(default=None, ge=1, le=5)

    typical_crowd_level: Optional[int] = Field(default=None, ge=1, le=5)
    is_hidden_gem: bool = False
    is_must_see: bool = False
    instagram_worthy: bool = False


class POIAttributesResponse(POIAttributesCreate):
    """Response schema for POI attributes."""

    poi_id: UUID

    class Config:
        from_attributes = True


class POIBase(BaseModel):
    """Base POI schema."""

    name: str
    description: Optional[str] = None

    # Location
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    address: Optional[str] = None
    neighborhood: Optional[str] = None
    city: str = "Rome"
    country: str = "Italy"

    # Classification
    category: Optional[str] = None
    subcategory: Optional[str] = None

    # Timing
    typical_duration_minutes: Optional[int] = None
    best_time_of_day: Optional[str] = None
    best_days: Optional[List[str]] = None
    seasonal_availability: Optional[List[str]] = None

    # Cost
    cost_level: Optional[int] = Field(default=None, ge=1, le=5)
    avg_cost_per_person: Optional[Decimal] = None
    cost_currency: str = "EUR"

    # Metadata
    source: Optional[str] = None
    source_id: Optional[str] = None


class POICreate(POIBase):
    """Create a new POI."""

    persona_scores: Optional[POIPersonaScoresCreate] = None
    attributes: Optional[POIAttributesCreate] = None


class POIUpdate(BaseModel):
    """Update an existing POI."""

    name: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    address: Optional[str] = None
    neighborhood: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    typical_duration_minutes: Optional[int] = None
    best_time_of_day: Optional[str] = None
    best_days: Optional[List[str]] = None
    seasonal_availability: Optional[List[str]] = None
    cost_level: Optional[int] = Field(default=None, ge=1, le=5)
    avg_cost_per_person: Optional[Decimal] = None


class POIResponse(POIBase):
    """Response schema for a POI."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class POIWithScoresResponse(POIResponse):
    """POI response with persona scores and attributes."""

    persona_scores: Optional[POIPersonaScoresResponse] = None
    attributes: Optional[POIAttributesResponse] = None

    class Config:
        from_attributes = True
