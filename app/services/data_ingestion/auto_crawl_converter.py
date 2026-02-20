"""
Converts ExtractedPOI objects from web_poi_crawler into POI dicts
suitable for seed_pois() insertion into the vector database.

Reuses scoring logic from sample_data_converter and adds source-specific
boosts and rating/review handling.
"""
import re
import logging
from typing import Dict, List

from app.services.data_ingestion.sample_data_converter import (
    _compute_persona_scores,
    _estimate_cost_level,
    _estimate_duration,
    _get_city_center,
    _get_city_metadata,
)
from app.services.data_ingestion.web_poi_crawler import (
    ExtractedPOI,
    SOURCE_BOOSTS,
)

logger = logging.getLogger(__name__)


def _normalize_title(title: str) -> str:
    """Normalize a title for deduplication."""
    return re.sub(r"[^a-z0-9]", "", title.lower())


def convert_extracted_pois(
    pois: List[ExtractedPOI],
    city_key: str,
    source_tag_prefix: str = "auto_crawl",
) -> List[dict]:
    """
    Convert extracted POIs into dicts compatible with seed_pois().

    Args:
        pois: List of ExtractedPOI from WebPOICrawler.
        city_key: Lowercase city key (e.g. 'rome').
        source_tag_prefix: Prefix for the source tag ("auto_crawl" or "url_crawl").

    Returns:
        List of POI dicts ready for seed_pois().
    """
    center_lat, center_lon = _get_city_center(city_key)
    meta = _get_city_metadata(city_key)
    city_name = city_key.replace("_", " ").title()

    results: List[dict] = []
    seen: set = set()

    for poi in pois:
        if not poi.name or not poi.name.strip():
            continue

        # Dedup by normalized title
        norm = _normalize_title(poi.name)
        if norm in seen or len(norm) < 3:
            continue
        seen.add(norm)

        category = poi.category or "attraction"
        title = poi.name.strip()
        description = poi.description.strip() if poi.description else ""

        # Compute base persona scores from category + keywords
        scores = _compute_persona_scores(category, title, description)

        # Apply source domain boosts
        domain = (poi.source_domain or "").lower()
        for boost_domain, boosts in SOURCE_BOOSTS.items():
            if boost_domain in domain:
                for field, delta in boosts.items():
                    if field in scores:
                        scores[field] = min(1.0, scores[field] + delta)
                break

        # Rating boost: >= 4.5 adds +0.10 to all scores
        if poi.rating and poi.rating >= 4.5:
            for field in scores:
                if field.startswith("score_"):
                    scores[field] = min(1.0, scores[field] + 0.10)

        # Attributes
        attributes = {}
        if poi.review_count and poi.review_count >= 1000:
            attributes["is_must_see"] = True
        if poi.rating:
            attributes["rating"] = poi.rating
        if poi.review_count:
            attributes["review_count"] = poi.review_count

        # Build source tag from domain
        domain_prefix = domain.split(".")[0] if domain else "unknown"
        source = f"{source_tag_prefix}_{domain_prefix}"

        result = {
            "name": title,
            "description": description or f"{title} in {city_name}",
            "latitude": center_lat,
            "longitude": center_lon,
            "city": city_name,
            "country": meta["country"],
            "category": category,
            "subcategory": poi.subcategory,
            "typical_duration_minutes": _estimate_duration(category, title, description),
            "best_time_of_day": "any",
            "cost_level": _estimate_cost_level(category, title, description),
            "cost_currency": meta["currency"],
            "source": source,
            "persona_scores": scores,
            "attributes": attributes,
        }
        results.append(result)

    logger.info(
        "Converted %d POIs for %s (from %d extracted, source=%s)",
        len(results), city_name, len(pois), source_tag_prefix,
    )
    return results
