"""
Converts CITY_ACTIVITIES from sample_itinerary_data.py into POI dicts
suitable for seed_pois() insertion into the vector database.
"""
import re
import logging
from typing import Dict, List

from app.core.country_config import CITY_BBOXES, COUNTRY_DATABASE

logger = logging.getLogger(__name__)

# Type mapping: sample activity type -> (POI category, subcategory)
TYPE_MAP = {
    "sightseeing": ("attraction", None),
    "meal": ("restaurant", None),
    "shopping": ("shopping", None),
}

# Types to skip entirely
SKIP_TYPES = {"hotel", "transport"}

# Base persona scores by POI category
BASE_SCORES_BY_CATEGORY: Dict[str, Dict[str, float]] = {
    "attraction": {
        "score_cultural": 0.70,
        "score_solo": 0.70,
        "score_couple": 0.70,
        "score_photography": 0.65,
        "score_friends": 0.65,
        "score_family": 0.60,
    },
    "restaurant": {
        "score_foodie": 0.80,
        "score_couple": 0.70,
        "score_friends": 0.70,
        "score_solo": 0.60,
    },
    "shopping": {
        "score_shopping": 0.85,
        "score_friends": 0.75,
        "score_solo": 0.65,
    },
}

# Keyword boost map: keyword -> {score_field: value}
KEYWORD_BOOSTS: Dict[str, Dict[str, float]] = {
    # Cultural
    "museum": {"score_cultural": 0.90, "score_solo": 0.85},
    "gallery": {"score_cultural": 0.90, "score_photography": 0.80},
    "cathedral": {"score_cultural": 0.85, "score_photography": 0.80},
    "basilica": {"score_cultural": 0.85, "score_photography": 0.80},
    "temple": {"score_cultural": 0.90, "score_photography": 0.85},
    "shrine": {"score_cultural": 0.90, "score_photography": 0.85},
    "palace": {"score_cultural": 0.85, "score_romantic": 0.75},
    "castle": {"score_cultural": 0.85, "score_adventure": 0.65},
    "ruins": {"score_cultural": 0.85, "score_adventure": 0.70},
    "forum": {"score_cultural": 0.85},
    "abbey": {"score_cultural": 0.85},
    "library": {"score_cultural": 0.85, "score_solo": 0.85},
    "monument": {"score_cultural": 0.80, "score_photography": 0.80},
    # Nature
    "garden": {"score_nature": 0.85, "score_relaxation": 0.80, "score_romantic": 0.75},
    "park": {"score_nature": 0.85, "score_relaxation": 0.80, "score_family": 0.80},
    "beach": {"score_nature": 0.85, "score_relaxation": 0.85, "score_family": 0.80},
    "viewpoint": {"score_photography": 0.90, "score_romantic": 0.80},
    "panoramic": {"score_photography": 0.90, "score_romantic": 0.80},
    "sunset": {"score_photography": 0.90, "score_romantic": 0.85},
    "hike": {"score_nature": 0.85, "score_adventure": 0.80},
    # Food
    "pizza": {"score_foodie": 0.85},
    "sushi": {"score_foodie": 0.85},
    "ramen": {"score_foodie": 0.85},
    "wine": {"score_foodie": 0.85, "score_romantic": 0.75},
    "market": {"score_foodie": 0.80, "score_shopping": 0.70},
    "bakery": {"score_foodie": 0.80},
    "cafe": {"score_foodie": 0.75, "score_relaxation": 0.70},
    "michelin": {"score_foodie": 0.95, "score_couple": 0.85},
    "trattoria": {"score_foodie": 0.85},
    "bistro": {"score_foodie": 0.80},
    "tapas": {"score_foodie": 0.85, "score_friends": 0.80},
    "seafood": {"score_foodie": 0.85},
    "steakhouse": {"score_foodie": 0.80, "score_friends": 0.80},
    "brunch": {"score_foodie": 0.75, "score_friends": 0.75},
    # Nightlife
    "bar": {"score_nightlife": 0.85, "score_friends": 0.80},
    "flamenco": {"score_nightlife": 0.80, "score_cultural": 0.85},
    "jazz": {"score_nightlife": 0.80, "score_cultural": 0.75},
    # Shopping
    "fashion": {"score_shopping": 0.90},
    "boutique": {"score_shopping": 0.85},
    "leather": {"score_shopping": 0.80},
    "vintage": {"score_shopping": 0.80, "score_adventure": 0.65},
    "souvenir": {"score_shopping": 0.70},
    # Family
    "kid": {"score_family": 0.85, "score_kids": 0.85},
    "family": {"score_family": 0.85, "score_kids": 0.80},
    # Romance
    "romantic": {"score_romantic": 0.90, "score_couple": 0.85},
    "hidden gem": {"score_adventure": 0.80, "score_romantic": 0.75},
    # Adventure
    "climb": {"score_adventure": 0.80},
    "rooftop": {"score_photography": 0.80, "score_romantic": 0.75},
    "underground": {"score_adventure": 0.80},
    "boat": {"score_adventure": 0.70, "score_romantic": 0.75},
    # Wellness
    "spa": {"score_wellness": 0.90, "score_relaxation": 0.85},
    "thermal": {"score_wellness": 0.90, "score_relaxation": 0.85},
    "onsen": {"score_wellness": 0.90, "score_relaxation": 0.85},
}

# Currency lookup from COUNTRY_DATABASE
_CURRENCY_BY_COUNTRY: Dict[str, str] = {}
for _cid, _cdata in COUNTRY_DATABASE.items():
    _CURRENCY_BY_COUNTRY[_cdata["name"]] = _cdata["currency"]


def _get_city_center(city_key: str) -> tuple:
    """Return (lat, lng) center of the city from CITY_BBOXES."""
    bbox = CITY_BBOXES.get(city_key, {})
    if not bbox:
        return (0.0, 0.0)
    lat = (bbox["min_lat"] + bbox["max_lat"]) / 2
    lon = (bbox["min_lon"] + bbox["max_lon"]) / 2
    return (round(lat, 6), round(lon, 6))


def _get_city_metadata(city_key: str) -> dict:
    """Return country and currency for a city."""
    bbox = CITY_BBOXES.get(city_key, {})
    country = bbox.get("country", "Unknown")
    currency = _CURRENCY_BY_COUNTRY.get(country, "EUR")
    return {"country": country, "currency": currency}


def _normalize_title(title: str) -> str:
    """Normalize a title for deduplication."""
    return re.sub(r"[^a-z0-9]", "", title.lower())


def _compute_persona_scores(category: str, title: str, description: str) -> dict:
    """Compute persona scores from base category + keyword boosts."""
    scores = {
        "score_family": 0.50, "score_kids": 0.50, "score_couple": 0.50,
        "score_honeymoon": 0.50, "score_solo": 0.50, "score_friends": 0.50,
        "score_seniors": 0.50, "score_business": 0.50,
        "score_adventure": 0.50, "score_relaxation": 0.50,
        "score_cultural": 0.50, "score_foodie": 0.50,
        "score_nightlife": 0.50, "score_nature": 0.50,
        "score_shopping": 0.50, "score_photography": 0.50,
        "score_wellness": 0.50, "score_romantic": 0.50,
    }

    # Apply base scores for category
    base = BASE_SCORES_BY_CATEGORY.get(category, {})
    for field, value in base.items():
        scores[field] = max(scores[field], value)

    # Scan text for keyword boosts
    text = f"{title} {description}".lower()
    for keyword, boosts in KEYWORD_BOOSTS.items():
        if keyword in text:
            for field, value in boosts.items():
                scores[field] = max(scores[field], value)

    return scores


def _estimate_duration(category: str, title: str, description: str) -> int:
    """Estimate typical visit duration in minutes."""
    text = f"{title} {description}".lower()
    if category == "restaurant":
        if any(w in text for w in ("brunch", "cafe", "coffee", "bakery", "pastry")):
            return 45
        return 75
    if category == "shopping":
        if "market" in text:
            return 90
        return 60
    # attraction
    if any(w in text for w in ("museum", "gallery", "palace", "castle")):
        return 120
    if any(w in text for w in ("park", "garden", "beach")):
        return 90
    if any(w in text for w in ("church", "cathedral", "basilica", "shrine")):
        return 45
    return 60


def _estimate_cost_level(category: str, title: str, description: str) -> int:
    """Estimate cost level 1-5."""
    text = f"{title} {description}".lower()
    if any(w in text for w in ("free", "no charge")):
        return 1
    if category == "restaurant":
        if any(w in text for w in ("michelin", "luxury", "upscale", "refined", "tasting menu")):
            return 4
        if any(w in text for w in ("legendary", "famous", "institution")):
            return 3
        if any(w in text for w in ("street food", "market", "stall", "cheap", "budget")):
            return 1
        return 2
    if category == "shopping":
        if any(w in text for w in ("luxury", "fashion", "designer", "flagship")):
            return 4
        return 2
    # attraction
    if any(w in text for w in ("free entry", "free admission")):
        return 1
    return 2


def convert_sample_activities(city_filter: str = None) -> List[dict]:
    """
    Convert CITY_ACTIVITIES into a list of POI dicts ready for seed_pois().

    Args:
        city_filter: Optional city key to convert only one city.

    Returns:
        List of POI dicts compatible with seed_pois() format.
    """
    from app.services.sample_itinerary_data import CITY_ACTIVITIES

    pois = []
    seen: Dict[str, set] = {}  # city -> set of normalized titles

    cities_to_process = (
        {city_filter: CITY_ACTIVITIES[city_filter]}
        if city_filter and city_filter in CITY_ACTIVITIES
        else CITY_ACTIVITIES
    )

    for city_key, days in cities_to_process.items():
        if city_key not in seen:
            seen[city_key] = set()

        center_lat, center_lon = _get_city_center(city_key)
        meta = _get_city_metadata(city_key)
        city_name = city_key.replace("_", " ").title()

        for day in days:
            for activity in day.get("activities", []):
                act_type = activity.get("type", "")
                if act_type in SKIP_TYPES:
                    continue

                mapping = TYPE_MAP.get(act_type)
                if not mapping:
                    continue

                category, subcategory = mapping
                title = activity.get("title", "")
                description = activity.get("description", "")

                if not title:
                    continue

                # Dedup by normalized title within city
                norm = _normalize_title(title)
                if norm in seen[city_key]:
                    continue
                seen[city_key].add(norm)

                # Build persona scores
                persona_scores = _compute_persona_scores(category, title, description)

                poi = {
                    "name": title,
                    "description": description or f"{title} in {city_name}",
                    "latitude": center_lat,
                    "longitude": center_lon,
                    "city": city_name,
                    "country": meta["country"],
                    "category": category,
                    "subcategory": subcategory,
                    "typical_duration_minutes": _estimate_duration(category, title, description),
                    "best_time_of_day": "any",
                    "cost_level": _estimate_cost_level(category, title, description),
                    "cost_currency": meta["currency"],
                    "source": "sample_itinerary",
                    "persona_scores": persona_scores,
                    "attributes": {
                        "is_must_see": True if category == "attraction" else False,
                    },
                }

                pois.append(poi)

    logger.info(f"Converted {len(pois)} POIs from sample itinerary data"
                f" ({len(cities_to_process)} cities)")
    return pois
