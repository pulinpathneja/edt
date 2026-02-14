"""
Seed Sample Data Script for EDT

Creates sample POIs, trip requests, and itineraries for Rome, Paris, and Tokyo.
Run: python -m scripts.seed_sample_data
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
import random
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://edt_user:EdtSecure2024@34.46.220.220:5432/edt_db"
)

# Sample POIs for each city
SAMPLE_POIS = {
    "rome": [
        {
            "name": "Colosseum",
            "description": "Ancient Roman amphitheater, icon of Imperial Rome and one of the New Seven Wonders of the World",
            "latitude": 41.8902,
            "longitude": 12.4922,
            "neighborhood": "Centro Storico",
            "category": "attraction",
            "subcategory": "historical",
            "typical_duration_minutes": 120,
            "best_time_of_day": "morning",
            "cost_level": 3,
            "avg_cost_per_person": 18.00,
            "is_must_see": True,
            "scores": {"cultural": 0.95, "romantic": 0.70, "photography": 0.95, "family": 0.85}
        },
        {
            "name": "Trevi Fountain",
            "description": "Baroque masterpiece and the largest fountain in Rome. Toss a coin to ensure your return to the Eternal City",
            "latitude": 41.9009,
            "longitude": 12.4833,
            "neighborhood": "Trevi",
            "category": "attraction",
            "subcategory": "monument",
            "typical_duration_minutes": 45,
            "best_time_of_day": "evening",
            "cost_level": 1,
            "avg_cost_per_person": 0,
            "is_must_see": True,
            "scores": {"cultural": 0.85, "romantic": 0.98, "photography": 0.95, "nightlife": 0.70}
        },
        {
            "name": "Vatican Museums",
            "description": "World-renowned art collection including the Sistine Chapel with Michelangelo's ceiling",
            "latitude": 41.9065,
            "longitude": 12.4536,
            "neighborhood": "Vatican City",
            "category": "attraction",
            "subcategory": "museum",
            "typical_duration_minutes": 180,
            "best_time_of_day": "morning",
            "cost_level": 4,
            "avg_cost_per_person": 25.00,
            "is_must_see": True,
            "scores": {"cultural": 0.99, "romantic": 0.75, "photography": 0.80, "family": 0.70}
        },
        {
            "name": "Trastevere",
            "description": "Charming bohemian neighborhood with cobblestone streets, trattorias, and vibrant nightlife",
            "latitude": 41.8867,
            "longitude": 12.4692,
            "neighborhood": "Trastevere",
            "category": "activity",
            "subcategory": "neighborhood",
            "typical_duration_minutes": 150,
            "best_time_of_day": "evening",
            "cost_level": 2,
            "avg_cost_per_person": 35.00,
            "is_must_see": False,
            "scores": {"cultural": 0.75, "romantic": 0.90, "foodie": 0.95, "nightlife": 0.85}
        },
        {
            "name": "Pantheon",
            "description": "Best-preserved ancient Roman building with remarkable concrete dome and oculus",
            "latitude": 41.8986,
            "longitude": 12.4768,
            "neighborhood": "Centro Storico",
            "category": "attraction",
            "subcategory": "historical",
            "typical_duration_minutes": 60,
            "best_time_of_day": "any",
            "cost_level": 1,
            "avg_cost_per_person": 5.00,
            "is_must_see": True,
            "scores": {"cultural": 0.95, "romantic": 0.80, "photography": 0.85, "adventure": 0.40}
        },
    ],
    "paris": [
        {
            "name": "Eiffel Tower",
            "description": "Iconic iron lattice tower and symbol of Paris. Visit at sunset for breathtaking views",
            "latitude": 48.8584,
            "longitude": 2.2945,
            "neighborhood": "7th arrondissement",
            "category": "attraction",
            "subcategory": "landmark",
            "typical_duration_minutes": 120,
            "best_time_of_day": "evening",
            "cost_level": 3,
            "avg_cost_per_person": 28.00,
            "is_must_see": True,
            "scores": {"cultural": 0.90, "romantic": 0.99, "photography": 0.99, "family": 0.85}
        },
        {
            "name": "Louvre Museum",
            "description": "World's largest art museum, home to the Mona Lisa and Venus de Milo",
            "latitude": 48.8606,
            "longitude": 2.3376,
            "neighborhood": "1st arrondissement",
            "category": "attraction",
            "subcategory": "museum",
            "typical_duration_minutes": 240,
            "best_time_of_day": "morning",
            "cost_level": 3,
            "avg_cost_per_person": 17.00,
            "is_must_see": True,
            "scores": {"cultural": 0.99, "romantic": 0.75, "photography": 0.85, "family": 0.70}
        },
        {
            "name": "Montmartre",
            "description": "Artistic hilltop neighborhood with Sacré-Cœur basilica and charming streets",
            "latitude": 48.8867,
            "longitude": 2.3431,
            "neighborhood": "18th arrondissement",
            "category": "activity",
            "subcategory": "neighborhood",
            "typical_duration_minutes": 180,
            "best_time_of_day": "afternoon",
            "cost_level": 2,
            "avg_cost_per_person": 20.00,
            "is_must_see": True,
            "scores": {"cultural": 0.85, "romantic": 0.95, "photography": 0.90, "adventure": 0.60}
        },
        {
            "name": "Seine River Cruise",
            "description": "Romantic boat cruise past Paris landmarks including Notre-Dame and the Louvre",
            "latitude": 48.8588,
            "longitude": 2.3194,
            "neighborhood": "Seine",
            "category": "activity",
            "subcategory": "cruise",
            "typical_duration_minutes": 90,
            "best_time_of_day": "evening",
            "cost_level": 3,
            "avg_cost_per_person": 18.00,
            "is_must_see": False,
            "scores": {"cultural": 0.70, "romantic": 0.99, "photography": 0.90, "relaxation": 0.85}
        },
        {
            "name": "Le Marais Food Tour",
            "description": "Walking food tour through the historic Jewish quarter sampling pastries, falafel, and cheese",
            "latitude": 48.8559,
            "longitude": 2.3588,
            "neighborhood": "Le Marais",
            "category": "activity",
            "subcategory": "food_tour",
            "typical_duration_minutes": 180,
            "best_time_of_day": "morning",
            "cost_level": 4,
            "avg_cost_per_person": 95.00,
            "is_must_see": False,
            "scores": {"cultural": 0.80, "foodie": 0.99, "adventure": 0.70, "friends": 0.90}
        },
    ],
    "tokyo": [
        {
            "name": "Senso-ji Temple",
            "description": "Tokyo's oldest temple with iconic Thunder Gate and Nakamise shopping street",
            "latitude": 35.7148,
            "longitude": 139.7967,
            "neighborhood": "Asakusa",
            "category": "attraction",
            "subcategory": "temple",
            "typical_duration_minutes": 90,
            "best_time_of_day": "morning",
            "cost_level": 1,
            "avg_cost_per_person": 0,
            "is_must_see": True,
            "scores": {"cultural": 0.95, "photography": 0.90, "spiritual": 0.85, "family": 0.80}
        },
        {
            "name": "Shibuya Crossing",
            "description": "World's busiest pedestrian crossing with dazzling neon lights and energy",
            "latitude": 35.6595,
            "longitude": 139.7004,
            "neighborhood": "Shibuya",
            "category": "attraction",
            "subcategory": "landmark",
            "typical_duration_minutes": 45,
            "best_time_of_day": "evening",
            "cost_level": 1,
            "avg_cost_per_person": 0,
            "is_must_see": True,
            "scores": {"cultural": 0.80, "photography": 0.95, "nightlife": 0.90, "adventure": 0.85}
        },
        {
            "name": "TeamLab Borderless",
            "description": "Immersive digital art museum with stunning interactive light installations",
            "latitude": 35.6269,
            "longitude": 139.7839,
            "neighborhood": "Odaiba",
            "category": "attraction",
            "subcategory": "museum",
            "typical_duration_minutes": 180,
            "best_time_of_day": "any",
            "cost_level": 4,
            "avg_cost_per_person": 32.00,
            "is_must_see": True,
            "scores": {"cultural": 0.85, "photography": 0.99, "romantic": 0.90, "adventure": 0.85}
        },
        {
            "name": "Tsukiji Outer Market",
            "description": "Fresh sushi, seafood, and Japanese street food at this legendary market",
            "latitude": 35.6654,
            "longitude": 139.7707,
            "neighborhood": "Tsukiji",
            "category": "activity",
            "subcategory": "market",
            "typical_duration_minutes": 120,
            "best_time_of_day": "morning",
            "cost_level": 3,
            "avg_cost_per_person": 40.00,
            "is_must_see": False,
            "scores": {"foodie": 0.99, "cultural": 0.85, "adventure": 0.80, "photography": 0.75}
        },
        {
            "name": "Meiji Shrine",
            "description": "Peaceful Shinto shrine surrounded by 170-acre forest in the heart of Tokyo",
            "latitude": 35.6764,
            "longitude": 139.6993,
            "neighborhood": "Harajuku",
            "category": "attraction",
            "subcategory": "shrine",
            "typical_duration_minutes": 75,
            "best_time_of_day": "morning",
            "cost_level": 1,
            "avg_cost_per_person": 0,
            "is_must_see": True,
            "scores": {"cultural": 0.90, "spiritual": 0.95, "nature": 0.85, "relaxation": 0.80}
        },
    ],
}

SELECTION_REASONS = [
    "Iconic must-see attraction",
    "Perfect match for your romantic vibe",
    "Top-rated cultural experience",
    "Great for photography enthusiasts",
    "Highly recommended for couples",
    "Local favorite hidden gem",
    "Matches your foodie preferences",
    "Ideal for your pacing preference",
]


async def create_tables(engine):
    """Create tables if they don't exist."""
    async with engine.begin() as conn:
        # Check if tables exist and create if not
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS pois (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(255) NOT NULL,
                description TEXT,
                latitude NUMERIC(10,8),
                longitude NUMERIC(11,8),
                address TEXT,
                neighborhood VARCHAR(100),
                city VARCHAR(100),
                country VARCHAR(100),
                category VARCHAR(50),
                subcategory VARCHAR(50),
                typical_duration_minutes INTEGER,
                best_time_of_day VARCHAR(20),
                best_days TEXT[],
                seasonal_availability TEXT[],
                cost_level INTEGER,
                avg_cost_per_person NUMERIC(10,2),
                cost_currency VARCHAR(3) DEFAULT 'EUR',
                source VARCHAR(50) DEFAULT 'seed_data',
                created_at TIMESTAMP DEFAULT now(),
                updated_at TIMESTAMP DEFAULT now()
            )
        """))

        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS poi_persona_scores (
                poi_id UUID PRIMARY KEY REFERENCES pois(id) ON DELETE CASCADE,
                score_family NUMERIC(3,2),
                score_couple NUMERIC(3,2),
                score_solo NUMERIC(3,2),
                score_honeymoon NUMERIC(3,2),
                score_friends NUMERIC(3,2),
                score_kids NUMERIC(3,2),
                score_seniors NUMERIC(3,2),
                score_business NUMERIC(3,2),
                score_adventure NUMERIC(3,2),
                score_relaxation NUMERIC(3,2),
                score_cultural NUMERIC(3,2),
                score_foodie NUMERIC(3,2),
                score_nightlife NUMERIC(3,2),
                score_nature NUMERIC(3,2),
                score_shopping NUMERIC(3,2),
                score_photography NUMERIC(3,2),
                score_wellness NUMERIC(3,2),
                score_romantic NUMERIC(3,2),
                score_accessibility NUMERIC(3,2),
                score_indoor NUMERIC(3,2),
                score_spiritual NUMERIC(3,2)
            )
        """))

        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS poi_attributes (
                poi_id UUID PRIMARY KEY REFERENCES pois(id) ON DELETE CASCADE,
                is_kid_friendly BOOLEAN DEFAULT false,
                is_pet_friendly BOOLEAN DEFAULT false,
                is_wheelchair_accessible BOOLEAN DEFAULT false,
                is_must_see BOOLEAN DEFAULT false,
                is_hidden_gem BOOLEAN DEFAULT false,
                instagram_worthy BOOLEAN DEFAULT false
            )
        """))

        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS trip_requests (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID,
                destination_city VARCHAR(100),
                start_date DATE,
                end_date DATE,
                group_type VARCHAR(50),
                group_size INTEGER DEFAULT 2,
                has_kids BOOLEAN DEFAULT false,
                has_seniors BOOLEAN DEFAULT false,
                vibes TEXT[],
                budget_level INTEGER DEFAULT 3,
                daily_budget NUMERIC(10,2),
                pacing VARCHAR(20) DEFAULT 'moderate',
                created_at TIMESTAMP DEFAULT now()
            )
        """))

        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS itineraries (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                trip_request_id UUID REFERENCES trip_requests(id) ON DELETE CASCADE,
                total_estimated_cost NUMERIC(10,2),
                generation_method VARCHAR(50) DEFAULT 'seed_data',
                created_at TIMESTAMP DEFAULT now()
            )
        """))

        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS itinerary_days (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                itinerary_id UUID REFERENCES itineraries(id) ON DELETE CASCADE,
                day_number INTEGER,
                date DATE,
                theme VARCHAR(100),
                estimated_cost NUMERIC(10,2),
                pacing_score NUMERIC(3,2)
            )
        """))

        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS itinerary_items (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                itinerary_day_id UUID REFERENCES itinerary_days(id) ON DELETE CASCADE,
                poi_id UUID REFERENCES pois(id) ON DELETE SET NULL,
                sequence_order INTEGER,
                start_time TIME,
                end_time TIME,
                selection_reason TEXT,
                persona_match_score NUMERIC(3,2),
                travel_time_from_previous INTEGER DEFAULT 0,
                travel_mode VARCHAR(20) DEFAULT 'walk'
            )
        """))

        print("Tables created/verified successfully")


async def seed_pois(session: AsyncSession, city: str, pois: list) -> list:
    """Insert POIs and return their IDs."""
    poi_ids = []
    country_map = {"rome": "Italy", "paris": "France", "tokyo": "Japan"}

    for poi in pois:
        poi_id = str(uuid.uuid4())

        # Insert POI
        await session.execute(text("""
            INSERT INTO pois (id, name, description, latitude, longitude, neighborhood,
                city, country, category, subcategory, typical_duration_minutes,
                best_time_of_day, cost_level, avg_cost_per_person, source)
            VALUES (:id, :name, :description, :latitude, :longitude, :neighborhood,
                :city, :country, :category, :subcategory, :typical_duration_minutes,
                :best_time_of_day, :cost_level, :avg_cost_per_person, 'seed_data')
            ON CONFLICT DO NOTHING
        """), {
            "id": poi_id,
            "name": poi["name"],
            "description": poi["description"],
            "latitude": poi["latitude"],
            "longitude": poi["longitude"],
            "neighborhood": poi["neighborhood"],
            "city": city.capitalize(),
            "country": country_map.get(city, "Unknown"),
            "category": poi["category"],
            "subcategory": poi["subcategory"],
            "typical_duration_minutes": poi["typical_duration_minutes"],
            "best_time_of_day": poi["best_time_of_day"],
            "cost_level": poi["cost_level"],
            "avg_cost_per_person": poi["avg_cost_per_person"],
        })

        # Insert persona scores
        scores = poi.get("scores", {})
        await session.execute(text("""
            INSERT INTO poi_persona_scores (poi_id, score_cultural, score_romantic,
                score_photography, score_family, score_foodie, score_adventure,
                score_nightlife, score_relaxation, score_spiritual, score_nature,
                score_couple, score_solo, score_honeymoon, score_friends)
            VALUES (:poi_id, :cultural, :romantic, :photography, :family, :foodie,
                :adventure, :nightlife, :relaxation, :spiritual, :nature,
                :couple, :solo, :honeymoon, :friends)
            ON CONFLICT DO NOTHING
        """), {
            "poi_id": poi_id,
            "cultural": scores.get("cultural", 0.5),
            "romantic": scores.get("romantic", 0.5),
            "photography": scores.get("photography", 0.5),
            "family": scores.get("family", 0.5),
            "foodie": scores.get("foodie", 0.5),
            "adventure": scores.get("adventure", 0.5),
            "nightlife": scores.get("nightlife", 0.3),
            "relaxation": scores.get("relaxation", 0.5),
            "spiritual": scores.get("spiritual", 0.3),
            "nature": scores.get("nature", 0.3),
            "couple": scores.get("romantic", 0.5),
            "solo": 0.7,
            "honeymoon": scores.get("romantic", 0.5) * 1.1,
            "friends": scores.get("friends", 0.6),
        })

        # Insert attributes
        await session.execute(text("""
            INSERT INTO poi_attributes (poi_id, is_must_see, is_hidden_gem, instagram_worthy,
                is_kid_friendly, is_wheelchair_accessible)
            VALUES (:poi_id, :is_must_see, :is_hidden_gem, :instagram_worthy,
                :is_kid_friendly, :is_wheelchair_accessible)
            ON CONFLICT DO NOTHING
        """), {
            "poi_id": poi_id,
            "is_must_see": poi.get("is_must_see", False),
            "is_hidden_gem": not poi.get("is_must_see", False),
            "instagram_worthy": scores.get("photography", 0.5) > 0.8,
            "is_kid_friendly": scores.get("family", 0.5) > 0.7,
            "is_wheelchair_accessible": random.choice([True, False]),
        })

        poi_ids.append({"id": poi_id, **poi})

    print(f"  Seeded {len(poi_ids)} POIs for {city}")
    return poi_ids


async def seed_itinerary(session: AsyncSession, city: str, pois: list, days: int = 3):
    """Create a sample itinerary."""
    # Create trip request
    trip_id = str(uuid.uuid4())
    start_date = datetime.now().date() + timedelta(days=random.randint(7, 30))
    end_date = start_date + timedelta(days=days - 1)

    vibes = random.sample(["cultural", "romantic", "foodie", "photography", "adventure"], 2)
    group_type = random.choice(["couple", "solo", "friends", "family"])

    await session.execute(text("""
        INSERT INTO trip_requests (id, destination_city, start_date, end_date,
            group_type, group_size, vibes, budget_level, pacing)
        VALUES (:id, :city, :start_date, :end_date, :group_type, :group_size,
            :vibes, :budget_level, :pacing)
    """), {
        "id": trip_id,
        "city": city.capitalize(),
        "start_date": start_date,
        "end_date": end_date,
        "group_type": group_type,
        "group_size": 2 if group_type == "couple" else random.randint(1, 4),
        "vibes": vibes,
        "budget_level": random.randint(2, 4),
        "pacing": "moderate",
    })

    # Create itinerary
    itinerary_id = str(uuid.uuid4())
    total_cost = sum(p["avg_cost_per_person"] for p in pois) * 2

    await session.execute(text("""
        INSERT INTO itineraries (id, trip_request_id, total_estimated_cost, generation_method)
        VALUES (:id, :trip_id, :total_cost, 'seed_data')
    """), {
        "id": itinerary_id,
        "trip_id": trip_id,
        "total_cost": total_cost,
    })

    # Create days and items
    day_themes = {
        "rome": ["Ancient Rome", "Vatican & Art", "Local Life & Trastevere"],
        "paris": ["Iconic Paris", "Art & Culture", "Romantic Montmartre"],
        "tokyo": ["Traditional Tokyo", "Modern Marvels", "Food & Markets"],
    }

    themes = day_themes.get(city, ["Exploration Day"] * 3)
    shuffled_pois = pois.copy()
    random.shuffle(shuffled_pois)

    for day_num in range(1, min(days + 1, 4)):
        day_id = str(uuid.uuid4())
        day_date = start_date + timedelta(days=day_num - 1)

        await session.execute(text("""
            INSERT INTO itinerary_days (id, itinerary_id, day_number, date, theme, pacing_score)
            VALUES (:id, :itinerary_id, :day_number, :date, :theme, :pacing_score)
        """), {
            "id": day_id,
            "itinerary_id": itinerary_id,
            "day_number": day_num,
            "date": day_date,
            "theme": themes[day_num - 1] if day_num <= len(themes) else "Free Exploration",
            "pacing_score": round(random.uniform(0.7, 0.9), 2),
        })

        # Add 2-3 POIs per day
        day_pois = shuffled_pois[(day_num - 1) * 2: day_num * 2]
        start_hour = 9

        for seq, poi in enumerate(day_pois):
            duration_hours = poi["typical_duration_minutes"] / 60
            start_time = f"{start_hour:02d}:00"
            end_hour = int(start_hour + duration_hours)
            end_time = f"{end_hour:02d}:00"

            await session.execute(text("""
                INSERT INTO itinerary_items (id, itinerary_day_id, poi_id, sequence_order,
                    start_time, end_time, selection_reason, persona_match_score,
                    travel_time_from_previous, travel_mode)
                VALUES (:id, :day_id, :poi_id, :seq, :start_time, :end_time,
                    :reason, :match_score, :travel_time, :travel_mode)
            """), {
                "id": str(uuid.uuid4()),
                "day_id": day_id,
                "poi_id": poi["id"],
                "seq": seq + 1,
                "start_time": start_time,
                "end_time": end_time,
                "reason": random.choice(SELECTION_REASONS),
                "match_score": round(random.uniform(0.75, 0.95), 2),
                "travel_time": 15 if seq > 0 else 0,
                "travel_mode": random.choice(["walk", "transit"]),
            })

            start_hour = end_hour + 1  # 1 hour break

    print(f"  Created {days}-day itinerary for {city}")


async def main():
    """Main seeding function."""
    print("=" * 60)
    print("EDT Sample Data Seeder")
    print("=" * 60)
    print(f"\nConnecting to: {DATABASE_URL[:50]}...")

    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        # Create tables
        await create_tables(engine)

        async with async_session() as session:
            for city, pois in SAMPLE_POIS.items():
                print(f"\nSeeding {city.upper()}...")

                # Insert POIs
                poi_data = await seed_pois(session, city, pois)

                # Create sample itinerary
                await seed_itinerary(session, city, poi_data, days=3)

            await session.commit()

        print("\n" + "=" * 60)
        print("SUCCESS! Sample data seeded successfully.")
        print("=" * 60)
        print("\nSeeded data:")
        print(f"  - {sum(len(p) for p in SAMPLE_POIS.values())} POIs across 3 cities")
        print("  - 3 sample itineraries (Rome, Paris, Tokyo)")
        print("\nYou can now test the Flutter app with this data!")

    except Exception as e:
        print(f"\nERROR: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
