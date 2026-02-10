from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from uuid import UUID
from datetime import datetime


class NeighborhoodBase(BaseModel):
    """Base schema for neighborhood."""
    name: str
    lat: float
    lon: float
    vibes: List[str] = []
    best_for: List[str] = []


class NeighborhoodScore(NeighborhoodBase):
    """Neighborhood with persona score."""
    score: float = Field(ge=0, le=1)
    reasoning: str


class BoundingBox(BaseModel):
    """Geographic bounding box."""
    min_lon: float
    min_lat: float
    max_lon: float
    max_lat: float


class CityCenter(BaseModel):
    """City center coordinates."""
    lat: float
    lon: float


class CityBase(BaseModel):
    """Base city schema."""
    name: str
    country: str
    currency: str
    bbox: BoundingBox
    center: CityCenter
    neighborhoods: List[NeighborhoodBase] = []


class CityCreate(BaseModel):
    """Schema for creating a new city."""
    name: str
    country: str
    currency: str
    min_lon: float
    min_lat: float
    max_lon: float
    max_lat: float
    neighborhoods: Optional[List[NeighborhoodBase]] = None


class CityResponse(CityBase):
    """City response schema."""
    id: str  # city key (e.g., "paris")
    landmark_count: Optional[int] = None
    poi_count: Optional[int] = None


class CityListResponse(BaseModel):
    """Response for list of cities."""
    cities: List[CityResponse]
    total: int


class NeighborhoodRecommendRequest(BaseModel):
    """Request for neighborhood recommendations."""
    city: str
    group_type: str  # family, couple, solo, friends, honeymoon, seniors, business
    vibes: List[str]  # cultural, romantic, foodie, etc.


class NeighborhoodRecommendResponse(BaseModel):
    """Response for neighborhood recommendations."""
    city: str
    group_type: str
    recommendations: List[NeighborhoodScore]
