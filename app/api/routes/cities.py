from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pathlib import Path
import json

from app.schemas.city import (
    CityResponse,
    CityListResponse,
    CityCreate,
    NeighborhoodBase,
    NeighborhoodScore,
    NeighborhoodRecommendRequest,
    NeighborhoodRecommendResponse,
    BoundingBox,
    CityCenter,
)

router = APIRouter()

# City Database (same as notebook)
CITY_DATABASE = {
    "paris": {
        "name": "Paris",
        "country": "France",
        "currency": "EUR",
        "bbox": {"min_lon": 2.25, "min_lat": 48.81, "max_lon": 2.42, "max_lat": 48.91},
        "center": {"lat": 48.8566, "lon": 2.3522},
        "neighborhoods": [
            {"name": "Le Marais", "lat": 48.8566, "lon": 2.3622, "vibes": ["cultural", "shopping", "nightlife"], "best_for": ["couple", "solo", "friends"]},
            {"name": "Saint-Germain-des-Prés", "lat": 48.8539, "lon": 2.3338, "vibes": ["cultural", "romantic", "foodie"], "best_for": ["couple", "honeymoon"]},
            {"name": "Montmartre", "lat": 48.8867, "lon": 2.3431, "vibes": ["romantic", "cultural", "photography"], "best_for": ["couple", "honeymoon", "solo"]},
            {"name": "Latin Quarter", "lat": 48.8494, "lon": 2.3470, "vibes": ["cultural", "foodie", "nightlife"], "best_for": ["solo", "friends", "budget"]},
            {"name": "Champs-Élysées", "lat": 48.8698, "lon": 2.3076, "vibes": ["shopping", "cultural"], "best_for": ["family", "couple", "business"]},
            {"name": "Eiffel Tower / 7th", "lat": 48.8584, "lon": 2.2945, "vibes": ["romantic", "cultural", "photography"], "best_for": ["family", "couple", "honeymoon"]},
        ]
    },
    "rome": {
        "name": "Rome",
        "country": "Italy",
        "currency": "EUR",
        "bbox": {"min_lon": 12.40, "min_lat": 41.85, "max_lon": 12.55, "max_lat": 41.95},
        "center": {"lat": 41.9028, "lon": 12.4964},
        "neighborhoods": [
            {"name": "Centro Storico", "lat": 41.8986, "lon": 12.4769, "vibes": ["cultural", "foodie", "romantic"], "best_for": ["couple", "solo"]},
            {"name": "Trastevere", "lat": 41.8894, "lon": 12.4700, "vibes": ["foodie", "nightlife", "romantic"], "best_for": ["couple", "friends"]},
            {"name": "Vatican City", "lat": 41.9029, "lon": 12.4534, "vibes": ["cultural", "photography"], "best_for": ["family", "solo", "seniors"]},
            {"name": "Monti", "lat": 41.8956, "lon": 12.4939, "vibes": ["shopping", "foodie", "nightlife"], "best_for": ["solo", "friends"]},
        ]
    },
    "barcelona": {
        "name": "Barcelona",
        "country": "Spain",
        "currency": "EUR",
        "bbox": {"min_lon": 2.05, "min_lat": 41.32, "max_lon": 2.23, "max_lat": 41.47},
        "center": {"lat": 41.3851, "lon": 2.1734},
        "neighborhoods": [
            {"name": "Gothic Quarter", "lat": 41.3833, "lon": 2.1777, "vibes": ["cultural", "nightlife", "foodie"], "best_for": ["solo", "friends", "couple"]},
            {"name": "El Born", "lat": 41.3850, "lon": 2.1833, "vibes": ["shopping", "foodie", "cultural"], "best_for": ["couple", "friends"]},
            {"name": "Barceloneta", "lat": 41.3795, "lon": 2.1894, "vibes": ["beach", "relaxation", "foodie"], "best_for": ["family", "friends"]},
            {"name": "Gràcia", "lat": 41.4036, "lon": 2.1561, "vibes": ["local", "foodie", "relaxation"], "best_for": ["solo", "couple"]},
        ]
    },
    "tokyo": {
        "name": "Tokyo",
        "country": "Japan",
        "currency": "JPY",
        "bbox": {"min_lon": 139.55, "min_lat": 35.55, "max_lon": 139.85, "max_lat": 35.80},
        "center": {"lat": 35.6762, "lon": 139.6503},
        "neighborhoods": [
            {"name": "Shibuya", "lat": 35.6580, "lon": 139.7016, "vibes": ["shopping", "nightlife", "photography"], "best_for": ["friends", "solo"]},
            {"name": "Shinjuku", "lat": 35.6938, "lon": 139.7034, "vibes": ["nightlife", "shopping", "foodie"], "best_for": ["friends", "solo"]},
            {"name": "Asakusa", "lat": 35.7148, "lon": 139.7967, "vibes": ["cultural", "photography", "foodie"], "best_for": ["family", "couple", "seniors"]},
            {"name": "Ginza", "lat": 35.6717, "lon": 139.7649, "vibes": ["shopping", "foodie", "luxury"], "best_for": ["couple", "business"]},
        ]
    },
    "london": {
        "name": "London",
        "country": "UK",
        "currency": "GBP",
        "bbox": {"min_lon": -0.20, "min_lat": 51.45, "max_lon": 0.05, "max_lat": 51.55},
        "center": {"lat": 51.5074, "lon": -0.1278},
        "neighborhoods": [
            {"name": "Westminster", "lat": 51.4975, "lon": -0.1357, "vibes": ["cultural", "photography"], "best_for": ["family", "couple", "solo"]},
            {"name": "Soho", "lat": 51.5137, "lon": -0.1337, "vibes": ["nightlife", "foodie", "shopping"], "best_for": ["friends", "solo", "couple"]},
            {"name": "South Bank", "lat": 51.5055, "lon": -0.1146, "vibes": ["cultural", "photography", "foodie"], "best_for": ["family", "couple"]},
            {"name": "Shoreditch", "lat": 51.5246, "lon": -0.0794, "vibes": ["nightlife", "foodie", "art"], "best_for": ["friends", "solo"]},
        ]
    },
}


def _get_landmark_count(city_key: str) -> int:
    """Get landmark count from file."""
    landmarks_dir = Path(__file__).parent.parent.parent.parent / "data" / "landmarks"
    file_path = landmarks_dir / f"{city_key}_landmarks.json"
    if file_path.exists():
        with open(file_path, 'r') as f:
            return len(json.load(f))
    return 0


def _city_to_response(city_key: str, city_data: dict) -> CityResponse:
    """Convert city dict to response model."""
    return CityResponse(
        id=city_key,
        name=city_data["name"],
        country=city_data["country"],
        currency=city_data["currency"],
        bbox=BoundingBox(**city_data["bbox"]),
        center=CityCenter(**city_data["center"]),
        neighborhoods=[NeighborhoodBase(**nb) for nb in city_data["neighborhoods"]],
        landmark_count=_get_landmark_count(city_key),
    )


@router.get("/", response_model=CityListResponse)
async def list_cities():
    """
    List all available cities.

    Returns cities with their bounding boxes, neighborhoods, and landmark counts.
    """
    cities = [
        _city_to_response(key, data)
        for key, data in CITY_DATABASE.items()
    ]
    return CityListResponse(cities=cities, total=len(cities))


@router.get("/{city_id}", response_model=CityResponse)
async def get_city(city_id: str):
    """
    Get details for a specific city.

    - **city_id**: City identifier (e.g., "paris", "rome", "tokyo")
    """
    city_key = city_id.lower()
    if city_key not in CITY_DATABASE:
        raise HTTPException(
            status_code=404,
            detail=f"City '{city_id}' not found. Available: {list(CITY_DATABASE.keys())}"
        )

    return _city_to_response(city_key, CITY_DATABASE[city_key])


@router.post("/", response_model=CityResponse)
async def create_city(city: CityCreate):
    """
    Add a new city to the database.

    Provide bounding box coordinates and optionally neighborhoods.
    """
    city_key = city.name.lower()

    if city_key in CITY_DATABASE:
        raise HTTPException(
            status_code=400,
            detail=f"City '{city.name}' already exists"
        )

    city_data = {
        "name": city.name,
        "country": city.country,
        "currency": city.currency,
        "bbox": {
            "min_lon": city.min_lon,
            "min_lat": city.min_lat,
            "max_lon": city.max_lon,
            "max_lat": city.max_lat
        },
        "center": {
            "lat": (city.min_lat + city.max_lat) / 2,
            "lon": (city.min_lon + city.max_lon) / 2
        },
        "neighborhoods": [nb.model_dump() for nb in (city.neighborhoods or [])]
    }

    CITY_DATABASE[city_key] = city_data

    return _city_to_response(city_key, city_data)


@router.get("/{city_id}/neighborhoods", response_model=List[NeighborhoodBase])
async def get_neighborhoods(city_id: str):
    """
    Get all neighborhoods for a city.
    """
    city_key = city_id.lower()
    if city_key not in CITY_DATABASE:
        raise HTTPException(status_code=404, detail=f"City '{city_id}' not found")

    return [
        NeighborhoodBase(**nb)
        for nb in CITY_DATABASE[city_key]["neighborhoods"]
    ]


@router.post("/neighborhoods/recommend", response_model=NeighborhoodRecommendResponse)
async def recommend_neighborhoods(request: NeighborhoodRecommendRequest):
    """
    Get neighborhood recommendations based on persona.

    Scores neighborhoods based on group type and vibes,
    returning ranked recommendations with reasoning.
    """
    city_key = request.city.lower()
    if city_key not in CITY_DATABASE:
        raise HTTPException(status_code=404, detail=f"City '{request.city}' not found")

    city_data = CITY_DATABASE[city_key]
    scored_neighborhoods = []

    for nb in city_data["neighborhoods"]:
        score = 0.0
        reasons = []

        # Group type match
        best_for = nb.get("best_for", [])
        if request.group_type in best_for:
            score += 0.4
            reasons.append(f"Great for {request.group_type} travelers")
        elif any(g in best_for for g in ["all", request.group_type[:4]]):
            score += 0.2

        # Vibe overlap
        nb_vibes = set(nb.get("vibes", []))
        trip_vibes = set(request.vibes)
        matching_vibes = nb_vibes & trip_vibes

        if matching_vibes:
            vibe_score = len(matching_vibes) / len(trip_vibes) * 0.4
            score += vibe_score
            reasons.append(f"Matches {', '.join(matching_vibes)} vibes")

        # Base score
        score += 0.2

        scored_neighborhoods.append(NeighborhoodScore(
            name=nb["name"],
            lat=nb["lat"],
            lon=nb["lon"],
            vibes=nb.get("vibes", []),
            best_for=nb.get("best_for", []),
            score=min(score, 1.0),
            reasoning="; ".join(reasons) if reasons else "Central location"
        ))

    # Sort by score descending
    scored_neighborhoods.sort(key=lambda x: x.score, reverse=True)

    return NeighborhoodRecommendResponse(
        city=request.city,
        group_type=request.group_type,
        recommendations=scored_neighborhoods
    )
