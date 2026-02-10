"""
API routes for first-level itinerary recommendations.

Provides:
- Where to stay based on persona
- What to visit based on persona and trip duration
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.services.recommendations import (
    get_first_level_recommendations,
    FirstLevelItinerary,
    NeighborhoodRecommendation,
    POIRecommendation,
)


router = APIRouter()


# --- Request/Response Schemas ---

class FirstLevelRequest(BaseModel):
    """Request for first-level itinerary recommendations."""
    city: str = Field(..., description="Destination city (e.g., 'Paris', 'Rome')")
    num_days: int = Field(..., ge=1, le=30, description="Number of days for the trip")
    group_type: str = Field(..., description="Type of group: family, couple, solo, friends, honeymoon, seniors, business")
    vibes: List[str] = Field(..., description="Selected vibes: cultural, foodie, romantic, adventure, relaxation, nightlife, shopping, photography, nature, wellness")
    budget_level: int = Field(3, ge=1, le=5, description="Budget level from 1 (budget) to 5 (luxury)")
    pacing: str = Field("moderate", description="Trip pacing: slow, moderate, fast")
    has_kids: bool = Field(False, description="Whether the group includes children")
    has_seniors: bool = Field(False, description="Whether the group includes seniors")


class NeighborhoodResponse(BaseModel):
    """Neighborhood recommendation response."""
    name: str
    description: str
    center_lat: float
    center_lon: float
    match_score: float
    vibes: List[str]
    best_for: List[str]
    reasoning: str


class POIResponse(BaseModel):
    """POI recommendation response."""
    name: str
    description: str
    category: str
    subcategory: str
    neighborhood: str
    duration_minutes: int
    cost_level: int
    avg_cost: float
    match_score: float
    group_score: float
    vibe_score: float
    priority: str
    reasoning: str
    latitude: float
    longitude: float


class FirstLevelResponse(BaseModel):
    """First-level itinerary recommendations response."""
    city: str
    num_days: int
    group_type: str
    vibes: List[str]
    budget_level: int
    pacing: str

    # Recommendations
    stay_recommendations: List[NeighborhoodResponse]
    poi_recommendations: List[POIResponse]

    # Summary
    total_must_see: int
    estimated_daily_cost: float
    suggested_pois_per_day: int


# --- API Endpoints ---

@router.post("/first-level", response_model=FirstLevelResponse)
async def get_first_level_itinerary(
    request: FirstLevelRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Get first-level itinerary recommendations.

    This provides:
    1. **Where to Stay**: Top neighborhood recommendations based on your persona
    2. **What to Visit**: POIs ranked by persona match, with must-see highlights

    Use this before generating a detailed day-by-day itinerary to understand
    the best areas and attractions for your trip.
    """
    result = await get_first_level_recommendations(
        db=db,
        city=request.city,
        num_days=request.num_days,
        group_type=request.group_type,
        vibes=request.vibes,
        budget_level=request.budget_level,
        pacing=request.pacing,
        has_kids=request.has_kids,
        has_seniors=request.has_seniors,
    )

    return FirstLevelResponse(
        city=result.city,
        num_days=result.num_days,
        group_type=result.group_type,
        vibes=result.vibes,
        budget_level=result.budget_level,
        pacing=result.pacing,
        stay_recommendations=[
            NeighborhoodResponse(
                name=n.name,
                description=n.description,
                center_lat=n.center_lat,
                center_lon=n.center_lon,
                match_score=n.match_score,
                vibes=n.vibes,
                best_for=n.best_for,
                reasoning=n.reasoning,
            )
            for n in result.stay_recommendations
        ],
        poi_recommendations=[
            POIResponse(
                name=p.name,
                description=p.description,
                category=p.category,
                subcategory=p.subcategory,
                neighborhood=p.neighborhood,
                duration_minutes=p.duration_minutes,
                cost_level=p.cost_level,
                avg_cost=p.avg_cost,
                match_score=p.match_score,
                group_score=p.group_score,
                vibe_score=p.vibe_score,
                priority=p.priority,
                reasoning=p.reasoning,
                latitude=p.latitude,
                longitude=p.longitude,
            )
            for p in result.poi_recommendations
        ],
        total_must_see=result.total_must_see,
        estimated_daily_cost=result.estimated_daily_cost,
        suggested_pois_per_day=result.suggested_pois_per_day,
    )


@router.get("/neighborhoods/{city}")
async def get_neighborhoods(
    city: str,
    group_type: Optional[str] = Query(None, description="Filter by group type"),
    vibes: Optional[List[str]] = Query(None, description="Filter by vibes"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all neighborhoods for a city with persona matching.

    Returns neighborhoods ranked by match score if group_type and vibes are provided.
    """
    from app.services.recommendations import RecommendationService

    service = RecommendationService(db)

    recommendations = service._get_stay_recommendations(
        city=city,
        group_type=group_type or "couple",
        vibes=vibes or ["cultural"],
        budget_level=3,
    )

    return {
        "city": city,
        "neighborhoods": [
            {
                "name": n.name,
                "description": n.description,
                "center_lat": n.center_lat,
                "center_lon": n.center_lon,
                "match_score": n.match_score,
                "vibes": n.vibes,
                "best_for": n.best_for,
                "reasoning": n.reasoning,
            }
            for n in recommendations
        ]
    }


@router.get("/cities")
async def list_available_cities(db: AsyncSession = Depends(get_db)):
    """
    List all cities available for itinerary generation.
    """
    from app.services.recommendations import RecommendationService

    service = RecommendationService(db)
    cities = list(service._neighborhood_data.keys())

    return {
        "cities": cities,
        "total": len(cities),
    }
