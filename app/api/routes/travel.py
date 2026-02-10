from typing import List
from fastapi import APIRouter
import math

from app.schemas.travel import (
    TravelTimeRequest,
    TravelTimeResponse,
    MultiPointTravelRequest,
    MultiPointTravelResponse,
    RouteLeg,
    OptimizeRouteRequest,
    OptimizeRouteResponse,
    Coordinates,
)

router = APIRouter()


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the distance between two points on Earth using Haversine formula.
    Returns distance in kilometers.
    """
    R = 6371  # Earth's radius in km

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c


def estimate_travel_time(lat1: float, lon1: float, lat2: float, lon2: float) -> dict:
    """
    Estimate travel time between two locations.

    Speeds:
    - Walking: 5 km/h (average tourist pace)
    - Transit/Metro: 25 km/h (including waiting + walking to station)
    """
    distance_km = haversine_distance(lat1, lon1, lat2, lon2)

    # Walking: 5 km/h average
    walk_hours = distance_km / 5.0
    walk_minutes = round(walk_hours * 60)

    # Transit: 25 km/h (accounts for waiting, walking to station)
    # Minimum 10 min for any transit
    transit_hours = distance_km / 25.0
    transit_minutes = max(10, round(transit_hours * 60))

    # Recommend mode based on distance
    if distance_km < 2.5:
        recommended = 'walk'
        recommended_time = walk_minutes
    else:
        recommended = 'transit'
        recommended_time = transit_minutes

    return {
        'distance_km': round(distance_km, 2),
        'walk_minutes': walk_minutes,
        'transit_minutes': transit_minutes,
        'recommended_mode': recommended,
        'recommended_time': recommended_time
    }


@router.post("/estimate", response_model=TravelTimeResponse)
async def calculate_travel_time(request: TravelTimeRequest):
    """
    Calculate travel time between two points.

    Returns walking time, transit time, and recommended mode.

    **Example:**
    ```json
    {
      "origin": {"latitude": 48.8584, "longitude": 2.2945},
      "destination": {"latitude": 48.8606, "longitude": 2.3376}
    }
    ```
    """
    result = estimate_travel_time(
        request.origin.latitude,
        request.origin.longitude,
        request.destination.latitude,
        request.destination.longitude
    )

    return TravelTimeResponse(**result)


@router.post("/route", response_model=MultiPointTravelResponse)
async def calculate_route_travel_time(request: MultiPointTravelRequest):
    """
    Calculate travel time for a multi-point route.

    Returns travel time for each leg and totals.

    **Example:**
    ```json
    {
      "points": [
        {"latitude": 48.8584, "longitude": 2.2945},
        {"latitude": 48.8606, "longitude": 2.3376},
        {"latitude": 48.8530, "longitude": 2.3499}
      ]
    }
    ```
    """
    legs = []
    total_distance = 0.0
    total_walk = 0
    total_transit = 0
    total_recommended = 0

    for i in range(len(request.points) - 1):
        p1 = request.points[i]
        p2 = request.points[i + 1]

        result = estimate_travel_time(
            p1.latitude, p1.longitude,
            p2.latitude, p2.longitude
        )

        legs.append(RouteLeg(
            from_index=i,
            to_index=i + 1,
            distance_km=result['distance_km'],
            walk_minutes=result['walk_minutes'],
            transit_minutes=result['transit_minutes'],
            recommended_mode=result['recommended_mode'],
            recommended_time=result['recommended_time']
        ))

        total_distance += result['distance_km']
        total_walk += result['walk_minutes']
        total_transit += result['transit_minutes']
        total_recommended += result['recommended_time']

    return MultiPointTravelResponse(
        legs=legs,
        total_distance_km=round(total_distance, 2),
        total_walk_minutes=total_walk,
        total_transit_minutes=total_transit,
        total_recommended_minutes=total_recommended
    )


@router.post("/optimize", response_model=OptimizeRouteResponse)
async def optimize_route(request: OptimizeRouteRequest):
    """
    Optimize the order of points to minimize total travel distance.

    Uses a greedy nearest-neighbor algorithm.
    Optionally fix start and/or end points.

    **Example:**
    ```json
    {
      "points": [
        {"latitude": 48.8584, "longitude": 2.2945},
        {"latitude": 48.8606, "longitude": 2.3376},
        {"latitude": 48.8530, "longitude": 2.3499},
        {"latitude": 48.8867, "longitude": 2.3431}
      ],
      "start_index": 0
    }
    ```
    """
    points = request.points
    n = len(points)

    # Calculate original distance
    original_distance = 0.0
    for i in range(n - 1):
        original_distance += haversine_distance(
            points[i].latitude, points[i].longitude,
            points[i+1].latitude, points[i+1].longitude
        )

    # Greedy nearest neighbor optimization
    start_idx = request.start_index or 0
    end_idx = request.end_index

    # Points to visit (excluding fixed start/end)
    to_visit = set(range(n))
    to_visit.discard(start_idx)
    if end_idx is not None:
        to_visit.discard(end_idx)

    optimized_order = [start_idx]
    current = start_idx

    while to_visit:
        # Find nearest unvisited point
        nearest = None
        nearest_dist = float('inf')

        for idx in to_visit:
            dist = haversine_distance(
                points[current].latitude, points[current].longitude,
                points[idx].latitude, points[idx].longitude
            )
            if dist < nearest_dist:
                nearest_dist = dist
                nearest = idx

        optimized_order.append(nearest)
        to_visit.discard(nearest)
        current = nearest

    # Add fixed end point if specified
    if end_idx is not None:
        optimized_order.append(end_idx)

    # Calculate optimized distance and legs
    optimized_distance = 0.0
    route_legs = []

    for i in range(len(optimized_order) - 1):
        idx1 = optimized_order[i]
        idx2 = optimized_order[i + 1]

        result = estimate_travel_time(
            points[idx1].latitude, points[idx1].longitude,
            points[idx2].latitude, points[idx2].longitude
        )

        route_legs.append(RouteLeg(
            from_index=idx1,
            to_index=idx2,
            distance_km=result['distance_km'],
            walk_minutes=result['walk_minutes'],
            transit_minutes=result['transit_minutes'],
            recommended_mode=result['recommended_mode'],
            recommended_time=result['recommended_time']
        ))

        optimized_distance += result['distance_km']

    savings = original_distance - optimized_distance
    savings_percent = (savings / original_distance * 100) if original_distance > 0 else 0

    return OptimizeRouteResponse(
        original_order=list(range(n)),
        optimized_order=optimized_order,
        original_total_km=round(original_distance, 2),
        optimized_total_km=round(optimized_distance, 2),
        savings_km=round(savings, 2),
        savings_percent=round(savings_percent, 1),
        route_legs=route_legs
    )


@router.get("/distance")
async def get_distance(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
):
    """
    Quick distance calculation between two coordinates (GET method).

    **Example:**
    `/travel/distance?lat1=48.8584&lon1=2.2945&lat2=48.8606&lon2=2.3376`
    """
    result = estimate_travel_time(lat1, lon1, lat2, lon2)
    return result
