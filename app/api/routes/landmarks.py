from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pathlib import Path
import json
import requests

from app.schemas.landmark import (
    LandmarkResponse,
    LandmarkListResponse,
    LandmarkGenerateRequest,
    LandmarkGenerateResponse,
    LandmarkCreate,
)

router = APIRouter()

# Base directory for landmark files
LANDMARKS_DIR = Path(__file__).parent.parent.parent.parent / "data" / "landmarks"


def load_landmarks_from_file(city: str) -> tuple[List[dict], str]:
    """Load landmarks from curated JSON file."""
    file_path = LANDMARKS_DIR / f"{city.lower()}_landmarks.json"

    if not file_path.exists():
        return [], "file_not_found"

    with open(file_path, 'r') as f:
        raw_landmarks = json.load(f)

    landmarks = []
    for i, lm in enumerate(raw_landmarks):
        landmarks.append({
            'id': lm.get('id', f'file_{i}'),
            'name': lm['name'],
            'category': lm.get('category', 'attraction'),
            'latitude': lm['latitude'],
            'longitude': lm['longitude'],
            'description': lm.get('description', ''),
            'address': lm.get('address', ''),
            'duration_minutes': lm.get('duration_minutes', 90),
            'must_see': lm.get('must_see', True),
            'family_friendly': lm.get('family_friendly', True),
            'family_only': lm.get('family_only', False),
            'confidence': 1.0,
            'is_famous': True,
        })

    return landmarks, "file"


def fetch_landmarks_from_wikidata(city_name: str, country: str, limit: int = 20) -> tuple[List[dict], str]:
    """Fetch famous landmarks from Wikidata SPARQL."""
    query = f"""
    SELECT DISTINCT ?place ?placeLabel ?placeDescription
           (SAMPLE(?coord) AS ?coordinate)
    WHERE {{
      VALUES ?type {{ wd:Q570116 wd:Q839954 wd:Q4989906 wd:Q33506 wd:Q811979 wd:Q16970 wd:Q57821 }}
      ?place wdt:P31/wdt:P279* ?type.
      ?place wdt:P131* ?location.
      ?location rdfs:label "{city_name}"@en.
      ?place wdt:P625 ?coord.
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    GROUP BY ?place ?placeLabel ?placeDescription
    LIMIT {limit}
    """

    try:
        response = requests.get(
            "https://query.wikidata.org/sparql",
            params={'query': query, 'format': 'json'},
            headers={'User-Agent': 'TravelItineraryBot/1.0'},
            timeout=30
        )
        data = response.json()

        landmarks = []
        for i, item in enumerate(data.get('results', {}).get('bindings', [])):
            name = item.get('placeLabel', {}).get('value', '')
            coord = item.get('coordinate', {}).get('value', '')
            desc = item.get('placeDescription', {}).get('value', '')

            if coord and name:
                try:
                    coord = coord.replace('Point(', '').replace(')', '')
                    lon, lat = map(float, coord.split())
                    landmarks.append({
                        'id': f'wikidata_{i}',
                        'name': name,
                        'category': 'attraction',
                        'latitude': lat,
                        'longitude': lon,
                        'description': desc[:200] if desc else f"Famous landmark in {city_name}",
                        'address': '',
                        'duration_minutes': 90,
                        'must_see': True,
                        'family_friendly': True,
                        'family_only': False,
                        'confidence': 1.0,
                        'is_famous': True,
                    })
                except:
                    pass

        return landmarks, "wikidata"
    except Exception as e:
        return [], f"wikidata_error: {str(e)}"


@router.get("/{city_id}", response_model=LandmarkListResponse)
async def get_landmarks(
    city_id: str,
    method: str = Query("auto", description="Method: auto, file, wikidata"),
    limit: int = Query(20, ge=1, le=50),
):
    """
    Get landmarks for a city.

    - **city_id**: City name (e.g., "paris", "rome")
    - **method**: Data source (auto, file, wikidata)
    - **limit**: Maximum landmarks to return

    Auto mode tries: file → wikidata
    """
    city = city_id.lower()
    landmarks = []
    source = "none"

    # Try file first
    if method in ["auto", "file"]:
        landmarks, source = load_landmarks_from_file(city)
        if landmarks:
            return LandmarkListResponse(
                city=city,
                country="",  # Could look up from city database
                landmarks=[LandmarkResponse(**lm) for lm in landmarks[:limit]],
                total=len(landmarks[:limit]),
                source=source
            )

    # Try Wikidata
    if method in ["auto", "wikidata"]:
        # Get country from city (simplified - could use city database)
        country_map = {
            "paris": "France",
            "rome": "Italy",
            "barcelona": "Spain",
            "tokyo": "Japan",
            "london": "UK",
        }
        country = country_map.get(city, "")

        landmarks, source = fetch_landmarks_from_wikidata(city.title(), country, limit)
        if landmarks:
            return LandmarkListResponse(
                city=city,
                country=country,
                landmarks=[LandmarkResponse(**lm) for lm in landmarks],
                total=len(landmarks),
                source=source
            )

    raise HTTPException(
        status_code=404,
        detail=f"No landmarks found for '{city_id}'. Try creating a landmarks file at data/landmarks/{city}_landmarks.json"
    )


@router.post("/generate", response_model=LandmarkGenerateResponse)
async def generate_landmarks(request: LandmarkGenerateRequest):
    """
    Generate landmarks for a city using specified method.

    Methods:
    - **auto**: Try file → wikidata → llm
    - **file**: Load from local file only
    - **wikidata**: Fetch from Wikidata SPARQL
    - **llm**: Generate using LLM (requires API key)
    """
    city = request.city.lower()
    landmarks = []
    method_used = "none"

    # Try file
    if request.method in ["auto", "file"]:
        landmarks, method_used = load_landmarks_from_file(city)
        if landmarks:
            return LandmarkGenerateResponse(
                city=request.city,
                country=request.country,
                landmarks=[LandmarkResponse(**lm) for lm in landmarks[:request.limit]],
                total=len(landmarks[:request.limit]),
                method_used="file",
                saved_to_file=True
            )

    # Try Wikidata
    if request.method in ["auto", "wikidata"]:
        landmarks, method_used = fetch_landmarks_from_wikidata(
            request.city, request.country, request.limit
        )
        if landmarks:
            return LandmarkGenerateResponse(
                city=request.city,
                country=request.country,
                landmarks=[LandmarkResponse(**lm) for lm in landmarks],
                total=len(landmarks),
                method_used="wikidata",
                saved_to_file=False
            )

    raise HTTPException(
        status_code=404,
        detail=f"Could not generate landmarks for '{request.city}' using method '{request.method}'"
    )


@router.post("/{city_id}", response_model=LandmarkResponse)
async def add_landmark(city_id: str, landmark: LandmarkCreate):
    """
    Add a landmark to a city's landmark file.
    """
    city = city_id.lower()
    file_path = LANDMARKS_DIR / f"{city}_landmarks.json"

    # Load existing landmarks
    existing = []
    if file_path.exists():
        with open(file_path, 'r') as f:
            existing = json.load(f)

    # Create new landmark
    new_landmark = {
        'id': f'{city}_{len(existing)}',
        'name': landmark.name,
        'category': landmark.category,
        'latitude': landmark.latitude,
        'longitude': landmark.longitude,
        'description': landmark.description or f"Landmark in {city.title()}",
        'duration_minutes': landmark.duration_minutes,
        'must_see': landmark.must_see,
        'family_friendly': landmark.family_friendly,
        'family_only': landmark.family_only,
    }

    existing.append(new_landmark)

    # Ensure directory exists
    LANDMARKS_DIR.mkdir(parents=True, exist_ok=True)

    # Save
    with open(file_path, 'w') as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

    return LandmarkResponse(
        id=new_landmark['id'],
        name=new_landmark['name'],
        category=new_landmark['category'],
        latitude=new_landmark['latitude'],
        longitude=new_landmark['longitude'],
        description=new_landmark['description'],
        duration_minutes=new_landmark['duration_minutes'],
        must_see=new_landmark['must_see'],
        family_friendly=new_landmark['family_friendly'],
        family_only=new_landmark['family_only'],
        confidence=1.0,
        is_famous=True
    )


@router.delete("/{city_id}/{landmark_id}")
async def delete_landmark(city_id: str, landmark_id: str):
    """
    Delete a landmark from a city's landmark file.
    """
    city = city_id.lower()
    file_path = LANDMARKS_DIR / f"{city}_landmarks.json"

    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"No landmarks file for '{city_id}'")

    with open(file_path, 'r') as f:
        landmarks = json.load(f)

    # Find and remove
    original_count = len(landmarks)
    landmarks = [lm for lm in landmarks if lm.get('id') != landmark_id]

    if len(landmarks) == original_count:
        raise HTTPException(status_code=404, detail=f"Landmark '{landmark_id}' not found")

    with open(file_path, 'w') as f:
        json.dump(landmarks, f, indent=2, ensure_ascii=False)

    return {"status": "deleted", "id": landmark_id, "city": city_id}
