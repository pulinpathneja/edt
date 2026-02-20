"""
Converts blog articles and TripAdvisor results from the city_insights table
into POI dicts suitable for seed_pois() insertion into the vector database.
"""
import re
import logging
from typing import Dict, List, Optional

from app.core.country_config import CITY_BBOXES, COUNTRY_DATABASE

logger = logging.getLogger(__name__)

# Currency lookup from COUNTRY_DATABASE
_CURRENCY_BY_COUNTRY: Dict[str, str] = {}
for _cid, _cdata in COUNTRY_DATABASE.items():
    _CURRENCY_BY_COUNTRY[_cdata["name"]] = _cdata["currency"]

# Listicle / guide patterns to filter out blog articles
_LISTICLE_PATTERN = re.compile(r"^\d+\s+(best|top|things)", re.IGNORECASE)
_GUIDE_PATTERN = re.compile(r"travel guide|itinerary|tips", re.IGNORECASE)

# TripAdvisor aggregate page patterns
_TA_AGGREGATE_PATTERN = re.compile(r"THE \d+ BEST|Top \d+", re.IGNORECASE)
# TripAdvisor suffix to strip from titles
_TA_SUFFIX_PATTERN = re.compile(
    r"\s*[-–—]\s*(?:\w[\w\s]*,\s*\w[\w\s]*\s*[-–—]\s*)?Tripadvisor.*$",
    re.IGNORECASE,
)

# Blog source -> persona boosts
BLOG_SOURCE_BOOSTS: Dict[str, Dict[str, float]] = {
    "Atlas Obscura": {"score_adventure": 0.15},
    "atlas_obscura": {"score_adventure": 0.15},
    "Eater": {"score_foodie": 0.20},
    "eater": {"score_foodie": 0.20},
    "Trekaroo": {"score_family": 0.15, "score_kids": 0.15},
    "trekaroo": {"score_family": 0.15, "score_kids": 0.15},
}

# Blog category -> (POI category, subcategory)
BLOG_CATEGORY_MAP: Dict[str, tuple] = {
    "hidden_gems": ("attraction", "hidden_gem"),
    "food": ("restaurant", None),
    "culture": ("attraction", "cultural"),
    "things_to_do": ("attraction", None),
    "neighborhoods": ("attraction", "neighborhood"),
}

# TripAdvisor category -> (POI category, subcategory)
TA_CATEGORY_MAP: Dict[str, tuple] = {
    "things_to_do": ("attraction", None),
    "restaurants": ("restaurant", None),
    "hidden_gems": ("attraction", "hidden_gem"),
}


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


def _base_scores() -> dict:
    """Return default 0.50 persona scores."""
    return {
        "score_family": 0.50, "score_kids": 0.50, "score_couple": 0.50,
        "score_honeymoon": 0.50, "score_solo": 0.50, "score_friends": 0.50,
        "score_seniors": 0.50, "score_business": 0.50,
        "score_adventure": 0.50, "score_relaxation": 0.50,
        "score_cultural": 0.50, "score_foodie": 0.50,
        "score_nightlife": 0.50, "score_nature": 0.50,
        "score_shopping": 0.50, "score_photography": 0.50,
        "score_wellness": 0.50, "score_romantic": 0.50,
    }


def _normalize_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]", "", title.lower())


def convert_blog_insights(insights: list, city_key: str) -> List[dict]:
    """
    Convert blog CityInsight rows into POI dicts.

    Args:
        insights: List of CityInsight rows (or dicts) with source='blog'.
        city_key: Lowercase city key (e.g. 'rome').

    Returns:
        List of POI dicts compatible with seed_pois().
    """
    center_lat, center_lon = _get_city_center(city_key)
    meta = _get_city_metadata(city_key)
    city_name = city_key.replace("_", " ").title()

    pois = []
    seen = set()

    for insight in insights:
        title = getattr(insight, "title", None) or (insight.get("title") if isinstance(insight, dict) else "")
        content = getattr(insight, "content", None) or (insight.get("content") if isinstance(insight, dict) else "")
        category_raw = getattr(insight, "category", None) or (insight.get("category") if isinstance(insight, dict) else "general")
        author = getattr(insight, "author", None) or (insight.get("author") if isinstance(insight, dict) else "")

        if not title or not title.strip():
            continue

        # Filter: skip listicles and guides
        if _LISTICLE_PATTERN.search(title):
            continue
        if _GUIDE_PATTERN.search(title):
            continue

        # Dedup
        norm = _normalize_title(title)
        if norm in seen:
            continue
        seen.add(norm)

        # Map category
        cat_info = BLOG_CATEGORY_MAP.get(category_raw, ("attraction", None))
        poi_category, poi_subcategory = cat_info

        # Build scores
        scores = _base_scores()
        if poi_category == "restaurant":
            scores["score_foodie"] = max(scores["score_foodie"], 0.75)
        elif poi_category == "attraction":
            scores["score_cultural"] = max(scores["score_cultural"], 0.70)
            scores["score_photography"] = max(scores["score_photography"], 0.65)
        if poi_subcategory == "hidden_gem":
            scores["score_adventure"] = max(scores["score_adventure"], 0.75)

        # Source-specific boosts
        for source_name, boosts in BLOG_SOURCE_BOOSTS.items():
            if author and source_name.lower() in author.lower():
                for field, delta in boosts.items():
                    scores[field] = min(1.0, scores[field] + delta)

        attributes = {}
        if poi_subcategory == "hidden_gem":
            attributes["is_hidden_gem"] = True

        poi = {
            "name": title.strip(),
            "description": (content or "").strip()[:500] or f"{title} in {city_name}",
            "latitude": center_lat,
            "longitude": center_lon,
            "city": city_name,
            "country": meta["country"],
            "category": poi_category,
            "subcategory": poi_subcategory,
            "typical_duration_minutes": 75 if poi_category == "restaurant" else 60,
            "best_time_of_day": "any",
            "cost_level": 2,
            "cost_currency": meta["currency"],
            "source": "blog_crawl",
            "persona_scores": scores,
            "attributes": attributes,
        }
        pois.append(poi)

    logger.info(f"Converted {len(pois)} blog POIs for {city_name}")
    return pois


def convert_tripadvisor_insights(insights: list, city_key: str) -> List[dict]:
    """
    Convert TripAdvisor CityInsight rows into POI dicts.

    Args:
        insights: List of CityInsight rows (or dicts) with source='tripadvisor'.
        city_key: Lowercase city key (e.g. 'rome').

    Returns:
        List of POI dicts compatible with seed_pois().
    """
    center_lat, center_lon = _get_city_center(city_key)
    meta = _get_city_metadata(city_key)
    city_name = city_key.replace("_", " ").title()

    pois = []
    seen = set()

    for insight in insights:
        title = getattr(insight, "title", None) or (insight.get("title") if isinstance(insight, dict) else "")
        content = getattr(insight, "content", None) or (insight.get("content") if isinstance(insight, dict) else "")
        category_raw = getattr(insight, "category", None) or (insight.get("category") if isinstance(insight, dict) else "general")
        rating = getattr(insight, "rating", None) or (insight.get("rating") if isinstance(insight, dict) else None)
        metadata_ = getattr(insight, "metadata_", None) or (insight.get("metadata") if isinstance(insight, dict) else {})

        if not title or not title.strip():
            continue

        # Filter: skip forums
        if category_raw == "forums":
            continue

        # Filter: skip aggregate pages
        if _TA_AGGREGATE_PATTERN.search(title):
            continue

        # Clean title: strip TripAdvisor suffixes
        clean_title = _TA_SUFFIX_PATTERN.sub("", title).strip()
        if not clean_title:
            continue

        # Dedup
        norm = _normalize_title(clean_title)
        if norm in seen:
            continue
        seen.add(norm)

        # Map category
        cat_info = TA_CATEGORY_MAP.get(category_raw, ("attraction", None))
        poi_category, poi_subcategory = cat_info

        # Build scores
        scores = _base_scores()
        if poi_category == "restaurant":
            scores["score_foodie"] = max(scores["score_foodie"], 0.75)
            scores["score_couple"] = max(scores["score_couple"], 0.65)
        elif poi_category == "attraction":
            scores["score_cultural"] = max(scores["score_cultural"], 0.70)
            scores["score_photography"] = max(scores["score_photography"], 0.65)
        if poi_subcategory == "hidden_gem":
            scores["score_adventure"] = max(scores["score_adventure"], 0.75)

        attributes = {}
        if poi_subcategory == "hidden_gem":
            attributes["is_hidden_gem"] = True

        # Rating boosts
        if rating and rating >= 4.5:
            for field in scores:
                if field.startswith("score_"):
                    scores[field] = min(1.0, scores[field] + 0.10)

        review_count = (metadata_ or {}).get("review_count", 0) if metadata_ else 0
        if review_count and review_count >= 1000:
            attributes["is_must_see"] = True

        poi = {
            "name": clean_title,
            "description": (content or "").strip()[:500] or f"{clean_title} in {city_name}",
            "latitude": center_lat,
            "longitude": center_lon,
            "city": city_name,
            "country": meta["country"],
            "category": poi_category,
            "subcategory": poi_subcategory,
            "typical_duration_minutes": 75 if poi_category == "restaurant" else 60,
            "best_time_of_day": "any",
            "cost_level": 2,
            "cost_currency": meta["currency"],
            "source": "tripadvisor_crawl",
            "persona_scores": scores,
            "attributes": attributes,
        }
        pois.append(poi)

    logger.info(f"Converted {len(pois)} TripAdvisor POIs for {city_name}")
    return pois
