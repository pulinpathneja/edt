"""
Overture Maps data fetcher and database seeder service.
Extracts POIs from BigQuery (Overture Maps) and seeds them into Cloud SQL (pgvector).
"""
import json
import uuid
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

from app.core.country_config import CITY_BBOXES

logger = logging.getLogger(__name__)

# Default GCP project
DEFAULT_GCP_PROJECT = "gen-lang-client-0518072406"

# Garbage keywords to filter out low-quality POIs
GARBAGE_KEYWORDS = [
    "atm", "parking", "gas station", "petrol", "self service",
    "post office", "bank branch", "insurance", "dentist", "pharmacy",
    "laundry", "car wash", "tire", "auto repair", "locksmith",
    "storage", "moving", "plumber", "electrician",
]

# Category-to-persona mapping for heuristic scoring
CATEGORY_PERSONA_MAP = {
    "museum": {"cultural": 0.95, "solo": 0.90, "couple": 0.85, "photography": 0.80},
    "gallery": {"cultural": 0.95, "solo": 0.90, "couple": 0.85, "art": 0.90},
    "church": {"cultural": 0.90, "romantic": 0.75, "photography": 0.85},
    "cathedral": {"cultural": 0.90, "romantic": 0.75, "photography": 0.85},
    "park": {"nature": 0.95, "relaxation": 0.90, "family": 0.90, "kids": 0.85},
    "garden": {"nature": 0.95, "relaxation": 0.90, "romantic": 0.80, "photography": 0.85},
    "restaurant": {"foodie": 0.90, "couple": 0.80, "friends": 0.85},
    "cafe": {"foodie": 0.75, "solo": 0.90, "relaxation": 0.80},
    "bar": {"nightlife": 0.95, "friends": 0.90, "couple": 0.75},
    "nightclub": {"nightlife": 0.95, "friends": 0.95},
    "shop": {"shopping": 0.95, "friends": 0.80, "solo": 0.75},
    "market": {"shopping": 0.90, "foodie": 0.80, "photography": 0.75},
    "monument": {"cultural": 0.85, "photography": 0.90, "couple": 0.80},
    "landmark": {"cultural": 0.85, "photography": 0.90, "couple": 0.80},
    "hotel": {},
    "beach": {"relaxation": 0.95, "nature": 0.85, "family": 0.85},
}


@dataclass
class RawPOI:
    """Raw POI from Overture Maps."""
    id: str
    name: str
    category: str
    latitude: float
    longitude: float
    address: Optional[str] = None
    confidence: float = 0.7


class OvertureMapsFetcher:
    """Fetches POIs from Overture Maps via BigQuery."""

    def __init__(self, project_id: str = DEFAULT_GCP_PROJECT):
        self.project_id = project_id

    def fetch_pois(self, city_key: str, limit: int = 500) -> List[RawPOI]:
        """Fetch POIs for a city from Overture Maps (BigQuery)."""
        try:
            from google.cloud import bigquery
        except ImportError:
            raise RuntimeError("BigQuery not available. Install: pip install google-cloud-bigquery")

        city_lower = city_key.lower()
        if city_lower not in CITY_BBOXES:
            raise ValueError(f"City '{city_key}' not configured. Add bounding box to CITY_BBOXES.")

        bbox = CITY_BBOXES[city_lower]
        client = bigquery.Client(project=self.project_id)

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

        logger.info(f"Fetching POIs from Overture Maps for {city_key}...")
        result = client.query(query).to_dataframe()

        pois = []
        for _, row in result.iterrows():
            name = row["name"]
            # Filter garbage POIs
            if any(kw in name.lower() for kw in GARBAGE_KEYWORDS):
                continue

            pois.append(RawPOI(
                id=row["id"],
                name=name,
                category=row["category"] or "unknown",
                latitude=row["latitude"],
                longitude=row["longitude"],
                address=None,
                confidence=row.get("confidence", 0.7),
            ))

        logger.info(f"Fetched {len(pois)} POIs for {city_key}")
        return pois

    def score_pois(self, raw_pois: List[RawPOI], city_key: str) -> List[Dict[str, Any]]:
        """Score raw POIs with persona scores using heuristics."""
        city_config = CITY_BBOXES.get(city_key.lower(), {})
        country = city_config.get("country", "Unknown")

        processed = []
        for poi in raw_pois:
            category = poi.category.lower() if poi.category else "unknown"
            name = poi.name.lower()

            # Default persona scores
            scores = {
                "score_family": 0.5, "score_kids": 0.5,
                "score_couple": 0.5, "score_honeymoon": 0.5,
                "score_solo": 0.5, "score_friends": 0.5,
                "score_seniors": 0.5, "score_business": 0.5,
                "score_adventure": 0.5, "score_relaxation": 0.5,
                "score_cultural": 0.5, "score_foodie": 0.5,
                "score_nightlife": 0.5, "score_nature": 0.5,
                "score_shopping": 0.5, "score_photography": 0.5,
                "score_romantic": 0.5,
            }

            # Determine main category
            main_category = "other"
            subcategory = "general"
            duration = 60
            cost = 2

            # Apply category-based scoring
            for cat_key, score_map in CATEGORY_PERSONA_MAP.items():
                if cat_key in category:
                    for score_key, score_val in score_map.items():
                        full_key = f"score_{score_key}"
                        if full_key in scores:
                            scores[full_key] = max(scores[full_key], score_val)

                    # Set main category/subcategory
                    if cat_key in ("museum", "gallery", "church", "cathedral", "monument", "landmark"):
                        main_category = "attraction"
                        subcategory = cat_key
                        duration = 90 if cat_key == "museum" else 45
                        cost = 3 if cat_key == "museum" else 2
                    elif cat_key in ("restaurant",):
                        main_category = "restaurant"
                        subcategory = "restaurant"
                        duration = 75
                        cost = 3
                    elif cat_key in ("cafe",):
                        main_category = "restaurant"
                        subcategory = "cafe"
                        duration = 45
                        cost = 2
                    elif cat_key in ("bar", "nightclub"):
                        main_category = "restaurant"
                        subcategory = "bar"
                        duration = 90
                        cost = 3
                        scores["score_kids"] = 0.1
                        scores["score_family"] = 0.2
                    elif cat_key in ("park", "garden", "beach"):
                        main_category = "attraction"
                        subcategory = cat_key
                        duration = 90
                        cost = 1
                    elif cat_key in ("shop", "market"):
                        main_category = "shopping"
                        subcategory = cat_key
                        duration = 60
                        cost = 2
                    break

            # Boost famous landmarks
            famous_keywords = ["tower", "palace", "castle", "basilica", "cathedral", "colosseum", "vatican"]
            if any(kw in name for kw in famous_keywords):
                scores["score_photography"] = max(scores["score_photography"], 0.90)
                scores["score_cultural"] = max(scores["score_cultural"], 0.85)

            processed.append({
                "name": poi.name,
                "description": f"{poi.name} - {poi.category} in {city_key.title()}",
                "latitude": poi.latitude,
                "longitude": poi.longitude,
                "address": poi.address or "",
                "neighborhood": "",
                "city": city_key.title(),
                "country": country,
                "category": main_category,
                "subcategory": subcategory,
                "typical_duration_minutes": duration,
                "cost_level": cost,
                "avg_cost_per_person": cost * 10.0,
                "cost_currency": "EUR",
                "source": "overture_maps",
                "source_id": poi.id,
                "persona_scores": scores,
                "attributes": {
                    "is_kid_friendly": scores["score_kids"] > 0.5,
                    "is_wheelchair_accessible": True,
                    "requires_reservation": cost >= 3,
                    "is_indoor": subcategory in ("museum", "gallery", "restaurant", "cafe", "bar", "shop"),
                    "is_outdoor": subcategory in ("park", "garden", "beach", "monument", "landmark"),
                    "is_must_see": False,
                    "is_hidden_gem": False,
                    "instagram_worthy": scores["score_photography"] > 0.8,
                    "physical_intensity": 2,
                },
            })

        return processed


class DatabaseSeeder:
    """Seeds processed POIs into the database with embeddings."""

    def __init__(self, db_session):
        self.db = db_session

    async def seed_pois(self, scored_pois: List[Dict[str, Any]], city: str) -> int:
        """Insert scored POIs into the database. Returns count of inserted POIs."""
        from app.models.poi import POI, POIPersonaScores, POIAttributes
        from app.core.embeddings import create_poi_description_embedding

        inserted = 0
        for poi_data in scored_pois:
            # Check for duplicates by source_id
            from sqlalchemy import select
            stmt = select(POI).where(POI.source_id == poi_data["source_id"])
            result = await self.db.execute(stmt)
            if result.scalar_one_or_none():
                continue

            # Generate embedding
            embedding = create_poi_description_embedding(
                name=poi_data["name"],
                description=poi_data["description"],
                category=poi_data["category"],
                subcategory=poi_data["subcategory"],
                neighborhood=poi_data.get("neighborhood", ""),
            )

            # Create POI
            poi_id = uuid.uuid4()
            poi = POI(
                id=poi_id,
                name=poi_data["name"],
                description=poi_data["description"],
                latitude=poi_data["latitude"],
                longitude=poi_data["longitude"],
                address=poi_data.get("address"),
                neighborhood=poi_data.get("neighborhood"),
                city=poi_data["city"],
                country=poi_data["country"],
                category=poi_data["category"],
                subcategory=poi_data["subcategory"],
                typical_duration_minutes=poi_data.get("typical_duration_minutes"),
                cost_level=poi_data.get("cost_level"),
                avg_cost_per_person=poi_data.get("avg_cost_per_person"),
                cost_currency=poi_data.get("cost_currency", "EUR"),
                description_embedding=embedding,
                source=poi_data.get("source", "overture_maps"),
                source_id=poi_data.get("source_id"),
            )
            self.db.add(poi)

            # Create persona scores
            persona_data = poi_data.get("persona_scores", {})
            persona_scores = POIPersonaScores(poi_id=poi_id, **persona_data)
            self.db.add(persona_scores)

            # Create attributes
            attrs_data = poi_data.get("attributes", {})
            attributes = POIAttributes(poi_id=poi_id, **attrs_data)
            self.db.add(attributes)

            inserted += 1

        await self.db.flush()
        logger.info(f"Seeded {inserted} POIs for {city}")
        return inserted

    @staticmethod
    def save_seed_json(scored_pois: List[Dict[str, Any]], city: str, output_dir: Optional[Path] = None) -> Path:
        """Save processed POIs to a seed JSON file."""
        if output_dir is None:
            output_dir = Path(__file__).parent.parent.parent.parent / "data" / "seed"
        output_dir.mkdir(parents=True, exist_ok=True)

        city_config = CITY_BBOXES.get(city.lower(), {})
        seed_data = {
            "city": city.title(),
            "country": city_config.get("country", "Unknown"),
            "source": "Overture Maps via BigQuery",
            "total_pois": len(scored_pois),
            "pois": scored_pois,
        }

        output_file = output_dir / f"{city.lower()}_pois.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(seed_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved seed file to {output_file}")
        return output_file
