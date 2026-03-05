from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Literal
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


# ============== Enhanced Schemas (US-LANDMARK-001) ==============


class LandmarkVibeScores(BaseModel):
    """Vibe compatibility scores for a landmark (0.0-1.0)."""
    romantic: float = Field(0.5, ge=0, le=1)
    cultural: float = Field(0.5, ge=0, le=1)
    adventure: float = Field(0.5, ge=0, le=1)
    relaxation: float = Field(0.5, ge=0, le=1)
    foodie: float = Field(0.5, ge=0, le=1)
    nightlife: float = Field(0.5, ge=0, le=1)
    nature: float = Field(0.5, ge=0, le=1)
    shopping: float = Field(0.5, ge=0, le=1)
    photography: float = Field(0.5, ge=0, le=1)
    spiritual: float = Field(0.5, ge=0, le=1)


class LandmarkGroupScores(BaseModel):
    """Group type compatibility scores (0.0-1.0)."""
    family: float = Field(0.5, ge=0, le=1)
    honeymoon: float = Field(0.5, ge=0, le=1)
    solo: float = Field(0.5, ge=0, le=1)
    friends: float = Field(0.5, ge=0, le=1)
    seniors: float = Field(0.5, ge=0, le=1)
    business: float = Field(0.5, ge=0, le=1)


class MustSeeRating(BaseModel):
    """Must-see classification with tier."""
    is_must_see: bool = True
    tier: Literal["iconic", "recommended", "optional"] = "recommended"
    reason: str = ""


class LandmarkEnhanced(BaseModel):
    """Enhanced landmark with full scoring data."""
    id: str
    name: str
    category: str
    latitude: float
    longitude: float
    description: str = ""
    address: Optional[str] = None

    must_see_rating: MustSeeRating = Field(default_factory=MustSeeRating)
    vibe_scores: LandmarkVibeScores = Field(default_factory=LandmarkVibeScores)
    group_scores: LandmarkGroupScores = Field(default_factory=LandmarkGroupScores)

    duration_by_persona: Dict[str, int] = Field(default_factory=lambda: {"default": 90})
    best_time: Literal["morning", "afternoon", "evening", "any"] = "any"
    golden_hour_worthy: bool = False

    # Computed at query time
    match_score: Optional[float] = None
    selection_reason: Optional[str] = None


class ScoredLandmarkResponse(BaseModel):
    """Single scored landmark in response."""
    id: str
    name: str
    category: str
    latitude: float
    longitude: float
    description: str = ""
    address: Optional[str] = None

    must_see_rating: MustSeeRating
    vibe_scores: LandmarkVibeScores
    group_scores: LandmarkGroupScores
    duration_by_persona: Dict[str, int]
    best_time: str = "any"
    golden_hour_worthy: bool = False

    match_score: float
    selection_reason: str


class ScoredLandmarkListResponse(BaseModel):
    """Response for scored landmark list."""
    city: str
    vibes: List[str]
    group_type: str
    landmarks: List[ScoredLandmarkResponse]
    total: int
