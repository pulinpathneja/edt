from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID


class LandmarkBase(BaseModel):
    """Base schema for landmark."""
    name: str
    category: str  # monument, museum, church, park, attraction, palace
    latitude: float
    longitude: float
    description: Optional[str] = None
    duration_minutes: int = 90
    must_see: bool = True
    family_friendly: bool = True
    family_only: bool = False


class LandmarkCreate(LandmarkBase):
    """Schema for creating a landmark."""
    pass


class LandmarkResponse(LandmarkBase):
    """Landmark response schema."""
    id: str
    address: Optional[str] = None
    confidence: float = 1.0
    is_famous: bool = True


class LandmarkListResponse(BaseModel):
    """Response for list of landmarks."""
    city: str
    country: str
    landmarks: List[LandmarkResponse]
    total: int
    source: str  # file, wikidata, llm


class LandmarkGenerateRequest(BaseModel):
    """Request to generate landmarks for a city."""
    city: str
    country: str
    method: str = "auto"  # auto, file, wikidata, llm
    limit: int = Field(default=20, ge=1, le=50)


class LandmarkGenerateResponse(BaseModel):
    """Response for landmark generation."""
    city: str
    country: str
    landmarks: List[LandmarkResponse]
    total: int
    method_used: str
    saved_to_file: bool = False
