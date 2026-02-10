"""
Fetch POIs for any city from Overture Maps (BigQuery) and auto-generate persona scores.

Usage:
    python -m data.scripts.fetch_city_pois --city Paris --limit 500
    python -m data.scripts.fetch_city_pois --city Barcelona --limit 300

Requirements:
    pip install google-cloud-bigquery google-generativeai pandas
    gcloud auth application-default login
"""

import argparse
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import os

# Google Cloud
try:
    from google.cloud import bigquery
    BIGQUERY_AVAILABLE = True
except ImportError:
    BIGQUERY_AVAILABLE = False
    print("⚠️ Install: pip install google-cloud-bigquery db-dtypes")

# Gemini for persona scoring
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ Install: pip install google-generativeai")


# City bounding boxes (add more as needed)
CITY_BBOXES = {
    "paris": {"min_lon": 2.25, "min_lat": 48.81, "max_lon": 2.42, "max_lat": 48.91, "country": "France"},
    "rome": {"min_lon": 12.40, "min_lat": 41.85, "max_lon": 12.55, "max_lat": 41.95, "country": "Italy"},
    "barcelona": {"min_lon": 2.05, "min_lat": 41.32, "max_lon": 2.23, "max_lat": 41.47, "country": "Spain"},
    "london": {"min_lon": -0.20, "min_lat": 51.45, "max_lon": 0.05, "max_lat": 51.55, "country": "UK"},
    "tokyo": {"min_lon": 139.55, "min_lat": 35.55, "max_lon": 139.85, "max_lat": 35.80, "country": "Japan"},
    "new york": {"min_lon": -74.05, "min_lat": 40.68, "max_lon": -73.90, "max_lat": 40.85, "country": "USA"},
    "amsterdam": {"min_lon": 4.85, "min_lat": 52.34, "max_lon": 4.95, "max_lat": 52.40, "country": "Netherlands"},
    "lisbon": {"min_lon": -9.20, "min_lat": 38.70, "max_lon": -9.10, "max_lat": 38.78, "country": "Portugal"},
    "dubai": {"min_lon": 55.10, "min_lat": 25.05, "max_lon": 55.35, "max_lat": 25.30, "country": "UAE"},
    "singapore": {"min_lon": 103.80, "min_lat": 1.25, "max_lon": 103.90, "max_lat": 1.35, "country": "Singapore"},
}


@dataclass
class RawPOI:
    """Raw POI from Overture Maps"""
    id: str
    name: str
    category: str
    latitude: float
    longitude: float
    address: Optional[str] = None
    confidence: float = 0.7


def fetch_pois_from_overture(city: str, project_id: str, limit: int = 500) -> List[RawPOI]:
    """
    Fetch POIs from Overture Maps via BigQuery.

    Overture Maps is a FREE open dataset with global POI coverage.
    Dataset: bigquery-public-data.overture_maps.place
    """
    if not BIGQUERY_AVAILABLE:
        raise RuntimeError("BigQuery not available. Install: pip install google-cloud-bigquery")

    city_lower = city.lower()
    if city_lower not in CITY_BBOXES:
        raise ValueError(f"City '{city}' not configured. Add bounding box to CITY_BBOXES.")

    bbox = CITY_BBOXES[city_lower]

    client = bigquery.Client(project=project_id)

    # Simple query without addresses (complex nested schema causes issues)
    query = f"""
    SELECT
        id,
        names.primary AS name,
        categories.primary AS category,
        ST_Y(geometry) AS latitude,
        ST_X(geometry) AS longitude,
        confidence
    FROM
        `bigquery-public-data.overture_maps.place`
    WHERE
        ST_X(geometry) BETWEEN {bbox['min_lon']} AND {bbox['max_lon']}
        AND ST_Y(geometry) BETWEEN {bbox['min_lat']} AND {bbox['max_lat']}
        AND confidence > 0.6
        AND names.primary IS NOT NULL
        AND categories.primary IS NOT NULL
    ORDER BY confidence DESC
    LIMIT {limit}
    """

    print(f"🔄 Fetching POIs from Overture Maps for {city}...")

    result = client.query(query).to_dataframe()

    pois = []
    for _, row in result.iterrows():
        pois.append(RawPOI(
            id=row['id'],
            name=row['name'],
            category=row['category'] or 'unknown',
            latitude=row['latitude'],
            longitude=row['longitude'],
            address=None,  # Address field skipped due to complex schema
            confidence=row.get('confidence', 0.7)
        ))

    print(f"✅ Fetched {len(pois)} POIs")
    return pois


def generate_persona_scores_with_gemini(poi: RawPOI, city: str) -> Dict[str, Any]:
    """
    Use Gemini to generate persona scores for a POI.

    This analyzes the POI name, category, and context to determine
    how well it matches different traveler personas.
    """
    if not GEMINI_AVAILABLE:
        return generate_persona_scores_heuristic(poi)

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("⚠️ No GEMINI_API_KEY found, using heuristic scoring")
        return generate_persona_scores_heuristic(poi)

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""
You are a travel expert. Analyze this POI and generate persona match scores.

POI Details:
- Name: {poi.name}
- Category: {poi.category}
- City: {city}
- Address: {poi.address or 'Unknown'}

Generate scores from 0.0 to 1.0 for how well this POI matches each persona.
Consider the typical interests and constraints of each group.

Return ONLY a valid JSON object (no markdown, no explanation):
{{
    "category": "attraction|restaurant|cafe|bar|shopping|activity|hotel|other",
    "subcategory": "museum|church|monument|park|historical|fine_dining|bistro|cafe|etc",
    "typical_duration_minutes": 60,
    "cost_level": 2,
    "persona_scores": {{
        "score_family": 0.0-1.0,
        "score_kids": 0.0-1.0,
        "score_couple": 0.0-1.0,
        "score_honeymoon": 0.0-1.0,
        "score_solo": 0.0-1.0,
        "score_friends": 0.0-1.0,
        "score_seniors": 0.0-1.0,
        "score_business": 0.0-1.0,
        "score_adventure": 0.0-1.0,
        "score_relaxation": 0.0-1.0,
        "score_cultural": 0.0-1.0,
        "score_foodie": 0.0-1.0,
        "score_nightlife": 0.0-1.0,
        "score_nature": 0.0-1.0,
        "score_shopping": 0.0-1.0,
        "score_photography": 0.0-1.0,
        "score_romantic": 0.0-1.0
    }},
    "attributes": {{
        "is_kid_friendly": true|false,
        "is_wheelchair_accessible": true|false,
        "requires_reservation": true|false,
        "is_indoor": true|false,
        "is_outdoor": true|false,
        "is_must_see": true|false,
        "is_hidden_gem": true|false,
        "instagram_worthy": true|false,
        "physical_intensity": 1-5
    }},
    "description": "Brief 1-2 sentence description of this place"
}}
"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        # Clean up response (remove markdown if present)
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()

        return json.loads(text)
    except Exception as e:
        print(f"  ⚠️ Gemini failed for {poi.name}: {e}")
        return generate_persona_scores_heuristic(poi)


def generate_persona_scores_heuristic(poi: RawPOI) -> Dict[str, Any]:
    """
    Generate persona scores using rule-based heuristics.
    Fallback when LLM is not available.
    """
    category = poi.category.lower() if poi.category else 'unknown'
    name = poi.name.lower()

    # Default scores
    scores = {
        "score_family": 0.5,
        "score_kids": 0.5,
        "score_couple": 0.5,
        "score_honeymoon": 0.5,
        "score_solo": 0.5,
        "score_friends": 0.5,
        "score_seniors": 0.5,
        "score_business": 0.5,
        "score_adventure": 0.5,
        "score_relaxation": 0.5,
        "score_cultural": 0.5,
        "score_foodie": 0.5,
        "score_nightlife": 0.5,
        "score_nature": 0.5,
        "score_shopping": 0.5,
        "score_photography": 0.5,
        "score_romantic": 0.5,
    }

    # Determine main category and adjust scores
    main_category = "other"
    subcategory = "general"
    duration = 60
    cost = 2

    # Museums
    if any(x in category for x in ['museum', 'gallery', 'art']):
        main_category = "attraction"
        subcategory = "museum"
        duration = 120
        cost = 3
        scores.update({
            "score_cultural": 0.95,
            "score_couple": 0.85,
            "score_solo": 0.90,
            "score_seniors": 0.85,
            "score_family": 0.70,
            "score_kids": 0.50,
            "score_photography": 0.80,
        })

    # Churches/Religious
    elif any(x in category for x in ['church', 'cathedral', 'religious', 'worship']):
        main_category = "attraction"
        subcategory = "church"
        duration = 45
        cost = 1
        scores.update({
            "score_cultural": 0.90,
            "score_romantic": 0.75,
            "score_photography": 0.85,
            "score_seniors": 0.80,
        })

    # Parks/Nature
    elif any(x in category for x in ['park', 'garden', 'nature', 'outdoor']):
        main_category = "attraction"
        subcategory = "park"
        duration = 90
        cost = 1
        scores.update({
            "score_nature": 0.95,
            "score_relaxation": 0.90,
            "score_family": 0.90,
            "score_kids": 0.85,
            "score_romantic": 0.80,
            "score_photography": 0.85,
        })

    # Restaurants
    elif any(x in category for x in ['restaurant', 'dining', 'food']):
        main_category = "restaurant"
        subcategory = "restaurant"
        duration = 75
        cost = 3
        scores.update({
            "score_foodie": 0.90,
            "score_couple": 0.80,
            "score_friends": 0.85,
            "score_romantic": 0.75,
        })

    # Cafes
    elif any(x in category for x in ['cafe', 'coffee', 'bakery']):
        main_category = "restaurant"
        subcategory = "cafe"
        duration = 45
        cost = 2
        scores.update({
            "score_foodie": 0.75,
            "score_solo": 0.90,
            "score_relaxation": 0.80,
            "score_couple": 0.75,
        })

    # Bars/Nightlife
    elif any(x in category for x in ['bar', 'pub', 'nightclub', 'club']):
        main_category = "restaurant"
        subcategory = "bar"
        duration = 90
        cost = 3
        scores.update({
            "score_nightlife": 0.95,
            "score_friends": 0.90,
            "score_solo": 0.70,
            "score_couple": 0.75,
            "score_kids": 0.10,
            "score_family": 0.20,
        })

    # Shopping
    elif any(x in category for x in ['shop', 'store', 'retail', 'market', 'mall']):
        main_category = "shopping"
        subcategory = "shop"
        duration = 60
        cost = 2
        scores.update({
            "score_shopping": 0.95,
            "score_friends": 0.80,
            "score_solo": 0.75,
        })

    # Monuments/Landmarks
    elif any(x in category for x in ['monument', 'landmark', 'historic', 'memorial']):
        main_category = "attraction"
        subcategory = "monument"
        duration = 45
        cost = 2
        scores.update({
            "score_cultural": 0.85,
            "score_photography": 0.90,
            "score_couple": 0.80,
            "score_romantic": 0.75,
        })

    # Hotels
    elif any(x in category for x in ['hotel', 'accommodation', 'lodging']):
        main_category = "hotel"
        subcategory = "hotel"
        duration = 0
        cost = 3

    # Check for famous landmarks by name
    famous_keywords = ['tower', 'palace', 'castle', 'basilica', 'cathedral', 'louvre', 'colosseum', 'vatican']
    if any(kw in name for kw in famous_keywords):
        scores["score_photography"] = max(scores["score_photography"], 0.90)
        scores["score_cultural"] = max(scores["score_cultural"], 0.85)

    return {
        "category": main_category,
        "subcategory": subcategory,
        "typical_duration_minutes": duration,
        "cost_level": cost,
        "persona_scores": scores,
        "attributes": {
            "is_kid_friendly": scores["score_kids"] > 0.5,
            "is_wheelchair_accessible": True,
            "requires_reservation": cost >= 3,
            "is_indoor": subcategory in ['museum', 'restaurant', 'cafe', 'bar', 'shop'],
            "is_outdoor": subcategory in ['park', 'monument', 'landmark'],
            "is_must_see": False,
            "is_hidden_gem": False,
            "instagram_worthy": scores["score_photography"] > 0.8,
            "physical_intensity": 2,
        },
        "description": f"{poi.name} - {poi.category} in the area."
    }


def process_pois(
    pois: List[RawPOI],
    city: str,
    use_llm: bool = True,
    batch_size: int = 10
) -> List[Dict[str, Any]]:
    """
    Process raw POIs and generate persona scores.
    """
    city_config = CITY_BBOXES.get(city.lower(), {})
    country = city_config.get("country", "Unknown")

    processed = []
    total = len(pois)

    for i, poi in enumerate(pois):
        print(f"  Processing {i+1}/{total}: {poi.name[:40]}...")

        # Generate scores
        if use_llm:
            enriched = generate_persona_scores_with_gemini(poi, city)
        else:
            enriched = generate_persona_scores_heuristic(poi)

        # Build final POI object
        processed_poi = {
            "name": poi.name,
            "description": enriched.get("description", f"{poi.name} in {city}"),
            "latitude": poi.latitude,
            "longitude": poi.longitude,
            "address": poi.address or "",
            "neighborhood": "",  # Would need reverse geocoding
            "city": city.title(),
            "country": country,
            "category": enriched.get("category", "other"),
            "subcategory": enriched.get("subcategory", "general"),
            "typical_duration_minutes": enriched.get("typical_duration_minutes", 60),
            "cost_level": enriched.get("cost_level", 2),
            "avg_cost_per_person": enriched.get("cost_level", 2) * 10.0,
            "cost_currency": "EUR",
            "source": "overture_maps",
            "source_id": poi.id,
            "persona_scores": enriched.get("persona_scores", {}),
            "attributes": enriched.get("attributes", {}),
        }

        processed.append(processed_poi)

    return processed


def save_seed_file(pois: List[Dict], city: str, output_dir: Path):
    """Save processed POIs to a seed JSON file."""
    city_config = CITY_BBOXES.get(city.lower(), {})

    seed_data = {
        "city": city.title(),
        "country": city_config.get("country", "Unknown"),
        "source": "Overture Maps via BigQuery",
        "total_pois": len(pois),
        "pois": pois,
        "neighborhoods": [],  # Would need additional processing
        "persona_templates": [],  # Can add city-specific templates
    }

    output_file = output_dir / f"{city.lower()}_pois.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(seed_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved to {output_file}")
    return output_file


async def main():
    parser = argparse.ArgumentParser(description="Fetch POIs for a city from Overture Maps")
    parser.add_argument("--city", required=True, help="City name (e.g., Paris, Rome)")
    parser.add_argument("--limit", type=int, default=100, help="Max POIs to fetch")
    parser.add_argument("--project", default=None, help="GCP project ID")
    parser.add_argument("--use-llm", action="store_true", help="Use Gemini for persona scoring")
    parser.add_argument("--output", default=None, help="Output directory")

    args = parser.parse_args()

    # Validate city
    if args.city.lower() not in CITY_BBOXES:
        print(f"❌ City '{args.city}' not configured.")
        print(f"Available cities: {', '.join(CITY_BBOXES.keys())}")
        print("\nTo add a new city, add its bounding box to CITY_BBOXES in this script.")
        return

    # Get project ID
    project_id = args.project or os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT_ID")
    if not project_id:
        print("❌ No GCP project ID. Set --project or GOOGLE_CLOUD_PROJECT env var")
        return

    print(f"\n{'='*60}")
    print(f"Fetching POIs for {args.city.title()}")
    print(f"{'='*60}")

    # Step 1: Fetch from Overture Maps
    try:
        raw_pois = fetch_pois_from_overture(args.city, project_id, args.limit)
    except Exception as e:
        print(f"❌ Failed to fetch POIs: {e}")
        return

    if not raw_pois:
        print("❌ No POIs found")
        return

    # Step 2: Process and score POIs
    print(f"\n🔄 Processing {len(raw_pois)} POIs...")
    processed_pois = process_pois(raw_pois, args.city, use_llm=args.use_llm)

    # Step 3: Save seed file
    output_dir = Path(args.output) if args.output else Path(__file__).parent.parent / "seed"
    output_dir.mkdir(parents=True, exist_ok=True)

    save_seed_file(processed_pois, args.city, output_dir)

    print(f"\n{'='*60}")
    print("DONE!")
    print(f"{'='*60}")
    print(f"\nNext steps:")
    print(f"  1. Review the generated file")
    print(f"  2. Seed to database: python -m data.scripts.seed_data {args.city.lower()}")


if __name__ == "__main__":
    asyncio.run(main())
