"""
Seed POI data for all cities missing from the database.
Run with: python -m data.scripts.seed_all_cities [city]

For each city in COUNTRY_DATABASE missing POI data:
1. Fetch from Overture Maps via BigQuery
2. Score with heuristic persona scoring
3. Generate 384D embeddings
4. Insert into pois + poi_persona_scores + poi_attributes
5. Save JSON to data/seed/{city}_pois.json

Cities to seed: florence, venice, milan, nice, lyon, bordeaux,
    madrid, seville, granada, kyoto, osaka, hiroshima, london, edinburgh
"""

import asyncio
import sys
import logging
from typing import Optional, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.country_config import CITY_BBOXES, COUNTRY_DATABASE
from app.models.poi import POI
from app.services.data_ingestion.overture_fetcher import OvertureMapsFetcher, DatabaseSeeder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_all_city_keys() -> List[str]:
    """Get all city keys from COUNTRY_DATABASE."""
    cities = []
    for country_data in COUNTRY_DATABASE.values():
        for city_key in country_data["cities"]:
            if city_key in CITY_BBOXES:
                cities.append(city_key)
    return cities


async def get_cities_needing_seed(db: AsyncSession) -> List[str]:
    """Find cities that have no POIs in the database."""
    all_cities = get_all_city_keys()
    needs_seed = []

    for city_key in all_cities:
        city_name = city_key.title()
        stmt = select(func.count()).select_from(POI).where(POI.city == city_name)
        result = await db.execute(stmt)
        count = result.scalar()

        if count == 0:
            needs_seed.append(city_key)
            logger.info(f"  {city_name}: needs seeding (0 POIs)")
        else:
            logger.info(f"  {city_name}: already has {count} POIs")

    return needs_seed


async def seed_city(db: AsyncSession, fetcher: OvertureMapsFetcher, city_key: str) -> int:
    """Fetch, score, embed, and insert POIs for a single city."""
    logger.info(f"\n{'='*50}")
    logger.info(f"Seeding {city_key.title()}...")
    logger.info(f"{'='*50}")

    # 1. Fetch from Overture Maps
    logger.info(f"  Fetching POIs from Overture Maps...")
    try:
        raw_pois = fetcher.fetch_pois(city_key, limit=500)
    except Exception as e:
        logger.error(f"  Failed to fetch POIs for {city_key}: {e}")
        return 0

    logger.info(f"  Fetched {len(raw_pois)} raw POIs")

    if not raw_pois:
        logger.warning(f"  No POIs found for {city_key}")
        return 0

    # 2. Score with heuristic persona scoring
    logger.info(f"  Scoring POIs...")
    scored_pois = fetcher.score_pois(raw_pois, city_key)
    logger.info(f"  Scored {len(scored_pois)} POIs")

    # 3. Save seed JSON
    logger.info(f"  Saving seed JSON...")
    DatabaseSeeder.save_seed_json(scored_pois, city_key)

    # 4. Insert into database (embeddings generated inside seed_pois)
    logger.info(f"  Inserting into database with embeddings...")
    seeder = DatabaseSeeder(db)
    count = await seeder.seed_pois(scored_pois, city_key.title())
    await db.commit()

    logger.info(f"  Inserted {count} POIs for {city_key.title()}")
    return count


async def main(city_filter: Optional[str] = None):
    """Main function to seed POIs for all cities."""
    logger.info("=" * 60)
    logger.info("SEEDING POI DATA FOR ALL CITIES")
    logger.info("=" * 60)

    fetcher = OvertureMapsFetcher()

    async with AsyncSessionLocal() as db:
        if city_filter:
            # Seed specific city
            cities_to_seed = [city_filter.lower()]
            logger.info(f"Seeding specific city: {city_filter}")
        else:
            # Find cities needing seed
            logger.info("\nChecking which cities need seeding...")
            cities_to_seed = await get_cities_needing_seed(db)

        if not cities_to_seed:
            logger.info("All cities already have POI data!")
            return

        logger.info(f"\nCities to seed ({len(cities_to_seed)}):")
        for c in cities_to_seed:
            logger.info(f"  - {c.title()}")

        # Seed each city
        results = {}
        for city_key in cities_to_seed:
            try:
                count = await seed_city(db, fetcher, city_key)
                results[city_key] = count
            except Exception as e:
                logger.error(f"Error seeding {city_key}: {e}")
                results[city_key] = 0

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("SEEDING COMPLETE!")
    logger.info("=" * 60)

    total = 0
    for city_key, count in results.items():
        logger.info(f"  {city_key.title()}: {count} POIs")
        total += count

    logger.info(f"\n  TOTAL: {total} POIs across {len(results)} cities")


if __name__ == "__main__":
    city_filter = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(main(city_filter))
