"""
Script to seed the database with POIs and persona templates for all cities.
Run with: python -m data.scripts.seed_data [city]

Examples:
  python -m data.scripts.seed_data          # Seed all cities
  python -m data.scripts.seed_data paris    # Seed only Paris
  python -m data.scripts.seed_data rome     # Seed only Rome
"""

import json
import asyncio
import sys
from pathlib import Path
from decimal import Decimal
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.embeddings import create_poi_description_embedding
from app.models.poi import POI, POIPersonaScores, POIAttributes
from app.models.persona import PersonaTemplate


def get_seed_files(city_filter: Optional[str] = None) -> List[Path]:
    """Get all seed files, optionally filtered by city."""
    seed_dir = Path(__file__).parent.parent / "seed"

    if city_filter:
        # Look for specific city file
        city_file = seed_dir / f"{city_filter.lower()}_pois.json"
        if city_file.exists():
            return [city_file]
        else:
            print(f"Warning: No seed file found for city '{city_filter}'")
            return []

    # Return all *_pois.json files
    return list(seed_dir.glob("*_pois.json"))


async def load_seed_data(seed_file: Path) -> dict:
    """Load seed data from JSON file."""
    with open(seed_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


async def seed_pois(db: AsyncSession, pois_data: list, city: str = "Unknown") -> int:
    """Seed POIs with their persona scores and attributes."""
    count = 0

    for poi_data in pois_data:
        # Check if POI already exists (by name and city)
        stmt = select(POI).where(
            POI.name == poi_data["name"],
            POI.city == poi_data.get("city", city)
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            print(f"  Skipping existing POI: {poi_data['name']}")
            continue

        # Generate embedding
        embedding = create_poi_description_embedding(
            name=poi_data["name"],
            description=poi_data.get("description", ""),
            category=poi_data.get("category", ""),
            subcategory=poi_data.get("subcategory", ""),
            neighborhood=poi_data.get("neighborhood", ""),
        )

        # Create POI
        poi = POI(
            name=poi_data["name"],
            description=poi_data.get("description"),
            latitude=poi_data.get("latitude"),
            longitude=poi_data.get("longitude"),
            address=poi_data.get("address"),
            neighborhood=poi_data.get("neighborhood"),
            city=poi_data.get("city", city),
            country=poi_data.get("country", "Unknown"),
            category=poi_data.get("category"),
            subcategory=poi_data.get("subcategory"),
            typical_duration_minutes=poi_data.get("typical_duration_minutes"),
            best_time_of_day=poi_data.get("best_time_of_day"),
            best_days=poi_data.get("best_days"),
            seasonal_availability=poi_data.get("seasonal_availability"),
            cost_level=poi_data.get("cost_level"),
            avg_cost_per_person=Decimal(str(poi_data.get("avg_cost_per_person", 0))),
            cost_currency=poi_data.get("cost_currency", "EUR"),
            source=poi_data.get("source", "manual"),
            description_embedding=embedding,
        )

        db.add(poi)
        await db.flush()

        # Create persona scores
        if "persona_scores" in poi_data:
            scores = POIPersonaScores(poi_id=poi.id, **poi_data["persona_scores"])
            db.add(scores)

        # Create attributes
        if "attributes" in poi_data:
            attrs = POIAttributes(poi_id=poi.id, **poi_data["attributes"])
            db.add(attrs)

        count += 1
        print(f"  Added POI: {poi_data['name']}")

    await db.commit()
    return count


async def seed_persona_templates(db: AsyncSession, templates_data: list) -> int:
    """Seed persona templates."""
    count = 0

    for template_data in templates_data:
        # Check if template already exists
        stmt = select(PersonaTemplate).where(PersonaTemplate.name == template_data["name"])
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            print(f"  Skipping existing template: {template_data['name']}")
            continue

        template = PersonaTemplate(
            name=template_data["name"],
            group_type=template_data.get("group_type"),
            primary_vibes=template_data.get("primary_vibes"),
            default_pacing=template_data.get("default_pacing"),
            default_budget_level=template_data.get("default_budget_level"),
            weight_config=template_data.get("weight_config"),
            filter_rules=template_data.get("filter_rules"),
        )

        db.add(template)
        count += 1
        print(f"  Added template: {template_data['name']}")

    await db.commit()
    return count


async def seed_city(db: AsyncSession, seed_file: Path) -> dict:
    """Seed data from a single city file."""
    data = await load_seed_data(seed_file)
    city = data.get("city", seed_file.stem.replace("_pois", "").title())

    print(f"\n{'='*50}")
    print(f"Seeding {city}...")
    print(f"{'='*50}")

    # Seed POIs
    print(f"\nSeeding POIs for {city}...")
    poi_count = await seed_pois(db, data.get("pois", []), city)
    print(f"Added {poi_count} POIs for {city}")

    # Seed persona templates if present
    template_count = 0
    if "persona_templates" in data:
        print(f"\nSeeding persona templates for {city}...")
        template_count = await seed_persona_templates(db, data.get("persona_templates", []))
        print(f"Added {template_count} persona templates for {city}")

    return {
        "city": city,
        "pois": poi_count,
        "templates": template_count
    }


async def main(city_filter: Optional[str] = None):
    """Main function to seed all data."""
    seed_files = get_seed_files(city_filter)

    if not seed_files:
        print("No seed files found!")
        return

    print(f"Found {len(seed_files)} seed file(s):")
    for f in seed_files:
        print(f"  - {f.name}")

    results = []

    async with AsyncSessionLocal() as db:
        for seed_file in seed_files:
            try:
                result = await seed_city(db, seed_file)
                results.append(result)
            except Exception as e:
                print(f"Error seeding {seed_file.name}: {e}")
                continue

    # Print summary
    print(f"\n{'='*50}")
    print("SEEDING COMPLETE!")
    print(f"{'='*50}")

    total_pois = 0
    total_templates = 0

    for result in results:
        print(f"\n{result['city']}:")
        print(f"  POIs: {result['pois']}")
        print(f"  Templates: {result['templates']}")
        total_pois += result['pois']
        total_templates += result['templates']

    print(f"\nTOTAL:")
    print(f"  Cities: {len(results)}")
    print(f"  POIs: {total_pois}")
    print(f"  Templates: {total_templates}")


if __name__ == "__main__":
    # Get optional city filter from command line
    city_filter = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(main(city_filter))
