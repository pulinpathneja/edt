from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from decimal import Decimal


class NLQueryRequest(BaseModel):
    """Natural language query request."""

    query: str = Field(
        ..., min_length=1, max_length=500, description="Natural language search query"
    )
    limit: int = Field(10, ge=1, le=50, description="Maximum number of results")
    include_related: bool = Field(
        False, description="Include knowledge graph related POIs"
    )
    include_insights: bool = Field(
        False, description="Include city intelligence snippets"
    )


class ParsedIntentResponse(BaseModel):
    """Shows how the query was decomposed."""

    city: Optional[str] = None
    country: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    neighborhood: Optional[str] = None
    vibes: List[str] = []
    group_type: Optional[str] = None
    attributes: List[str] = []
    near_poi_name: Optional[str] = None
    cost_level: Optional[int] = None
    time_of_day: Optional[str] = None
    semantic_query: str = ""
    confidence: float = 0.0


class RelatedPOIResponse(BaseModel):
    """A related POI from the knowledge graph."""

    id: str
    name: str
    category: Optional[str] = None
    relationship_type: str
    strength: Optional[float] = None
    distance_meters: Optional[int] = None


class CityInsightResponse(BaseModel):
    """A city intelligence snippet."""

    title: Optional[str] = None
    source: Optional[str] = None
    category: Optional[str] = None
    content: Optional[str] = None
    url: Optional[str] = None


class NLQueryResultItem(BaseModel):
    """A single result from the natural language query."""

    id: UUID
    name: str
    description: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    neighborhood: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    cost_level: Optional[int] = None
    avg_cost_per_person: Optional[Decimal] = None
    typical_duration_minutes: Optional[int] = None
    best_time_of_day: Optional[str] = None

    # Scores
    final_score: float
    vector_score: float
    persona_score: float

    # Explanation
    match_reasons: List[str]
    matched_vibes: List[str] = []
    matched_attributes: List[str] = []

    # Optional enrichments
    related_pois: Optional[List[RelatedPOIResponse]] = None
    city_insights: Optional[List[CityInsightResponse]] = None

    class Config:
        from_attributes = True


class NLQueryResponse(BaseModel):
    """Response for natural language query."""

    query: str
    parsed_intent: ParsedIntentResponse
    results: List[NLQueryResultItem]
    total: int
