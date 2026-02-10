from pydantic import BaseModel, Field
from typing import Optional, List


class Coordinates(BaseModel):
    """Geographic coordinates."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class TravelTimeRequest(BaseModel):
    """Request to calculate travel time between two points."""
    origin: Coordinates
    destination: Coordinates


class TravelTimeResponse(BaseModel):
    """Response with travel time estimation."""
    distance_km: float
    walk_minutes: int
    transit_minutes: int
    recommended_mode: str  # walk or transit
    recommended_time: int  # minutes


class MultiPointTravelRequest(BaseModel):
    """Request to calculate travel time for multiple points (route)."""
    points: List[Coordinates] = Field(..., min_length=2)


class RouteLeg(BaseModel):
    """Single leg of a route."""
    from_index: int
    to_index: int
    distance_km: float
    walk_minutes: int
    transit_minutes: int
    recommended_mode: str
    recommended_time: int


class MultiPointTravelResponse(BaseModel):
    """Response with route travel times."""
    legs: List[RouteLeg]
    total_distance_km: float
    total_walk_minutes: int
    total_transit_minutes: int
    total_recommended_minutes: int


class OptimizeRouteRequest(BaseModel):
    """Request to optimize route order."""
    points: List[Coordinates] = Field(..., min_length=2, max_length=20)
    start_index: Optional[int] = 0  # Fixed starting point
    end_index: Optional[int] = None  # Fixed ending point (optional)


class OptimizeRouteResponse(BaseModel):
    """Response with optimized route."""
    original_order: List[int]
    optimized_order: List[int]
    original_total_km: float
    optimized_total_km: float
    savings_km: float
    savings_percent: float
    route_legs: List[RouteLeg]
