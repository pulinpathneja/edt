"""
Seed Knowledge Graph data: cities, neighborhoods, and POI proximity relationships.
Run with: python -m data.scripts.seed_knowledge_graph

Seeds all 5 countries (Italy, France, Spain, Japan, UK) with:
- City metadata (lat/lng, timezone, currency, transport, safety scores)
- Neighborhood data for key cities
- Auto-generated POI proximity relationships (Haversine < 500m -> NEAR_TO)
"""

import asyncio
import sys
import logging
from typing import Dict, List, Any
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.country_config import COUNTRY_DATABASE
from app.models.knowledge_graph import City, Neighborhood
from app.services.knowledge_graph import RelationshipBuilder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# City metadata enrichment (lat/lng, timezone, transport, safety, budgets)
CITY_METADATA: Dict[str, Dict[str, Any]] = {
    # Italy
    "rome": {
        "latitude": 41.9028, "longitude": 12.4964, "timezone": "Europe/Rome",
        "country_code": "IT", "primary_language": "Italian", "currency_code": "EUR",
        "has_metro": True, "has_tram": True, "has_bus": True, "has_bike_share": True,
        "is_walkable": True, "uber_available": True,
        "peak_season_months": [6, 7, 8], "shoulder_season_months": [4, 5, 9, 10],
        "off_season_months": [1, 2, 3, 11, 12],
        "safety_score": 0.75, "tourist_friendliness": 0.85, "english_proficiency": 0.55,
        "avg_daily_budget_budget": 60, "avg_daily_budget_midrange": 150, "avg_daily_budget_luxury": 400,
    },
    "florence": {
        "latitude": 43.7696, "longitude": 11.2558, "timezone": "Europe/Rome",
        "country_code": "IT", "primary_language": "Italian", "currency_code": "EUR",
        "has_metro": False, "has_tram": True, "has_bus": True, "has_bike_share": True,
        "is_walkable": True, "uber_available": False,
        "peak_season_months": [5, 6, 7, 8, 9], "shoulder_season_months": [4, 10],
        "off_season_months": [1, 2, 3, 11, 12],
        "safety_score": 0.82, "tourist_friendliness": 0.88, "english_proficiency": 0.55,
        "avg_daily_budget_budget": 65, "avg_daily_budget_midrange": 160, "avg_daily_budget_luxury": 380,
    },
    "venice": {
        "latitude": 45.4408, "longitude": 12.3155, "timezone": "Europe/Rome",
        "country_code": "IT", "primary_language": "Italian", "currency_code": "EUR",
        "has_metro": False, "has_tram": False, "has_bus": False, "has_bike_share": False,
        "is_walkable": True, "uber_available": False,
        "peak_season_months": [5, 6, 7, 8, 9], "shoulder_season_months": [2, 4, 10],
        "off_season_months": [1, 3, 11, 12],
        "safety_score": 0.88, "tourist_friendliness": 0.82, "english_proficiency": 0.50,
        "avg_daily_budget_budget": 80, "avg_daily_budget_midrange": 180, "avg_daily_budget_luxury": 450,
    },
    "milan": {
        "latitude": 45.4642, "longitude": 9.1900, "timezone": "Europe/Rome",
        "country_code": "IT", "primary_language": "Italian", "currency_code": "EUR",
        "has_metro": True, "has_tram": True, "has_bus": True, "has_bike_share": True,
        "is_walkable": True, "uber_available": True,
        "peak_season_months": [4, 5, 6, 9, 10], "shoulder_season_months": [3, 7, 11],
        "off_season_months": [1, 2, 8, 12],
        "safety_score": 0.78, "tourist_friendliness": 0.75, "english_proficiency": 0.60,
        "avg_daily_budget_budget": 70, "avg_daily_budget_midrange": 170, "avg_daily_budget_luxury": 420,
    },
    # France
    "paris": {
        "latitude": 48.8566, "longitude": 2.3522, "timezone": "Europe/Paris",
        "country_code": "FR", "primary_language": "French", "currency_code": "EUR",
        "has_metro": True, "has_tram": True, "has_bus": True, "has_bike_share": True,
        "is_walkable": True, "uber_available": True,
        "peak_season_months": [6, 7, 8], "shoulder_season_months": [4, 5, 9, 10],
        "off_season_months": [1, 2, 3, 11, 12],
        "safety_score": 0.72, "tourist_friendliness": 0.80, "english_proficiency": 0.55,
        "avg_daily_budget_budget": 75, "avg_daily_budget_midrange": 180, "avg_daily_budget_luxury": 500,
    },
    "nice": {
        "latitude": 43.7102, "longitude": 7.2620, "timezone": "Europe/Paris",
        "country_code": "FR", "primary_language": "French", "currency_code": "EUR",
        "has_metro": False, "has_tram": True, "has_bus": True, "has_bike_share": True,
        "is_walkable": True, "uber_available": True,
        "peak_season_months": [6, 7, 8], "shoulder_season_months": [5, 9, 10],
        "off_season_months": [1, 2, 3, 4, 11, 12],
        "safety_score": 0.78, "tourist_friendliness": 0.82, "english_proficiency": 0.50,
        "avg_daily_budget_budget": 65, "avg_daily_budget_midrange": 160, "avg_daily_budget_luxury": 400,
    },
    "lyon": {
        "latitude": 45.7640, "longitude": 4.8357, "timezone": "Europe/Paris",
        "country_code": "FR", "primary_language": "French", "currency_code": "EUR",
        "has_metro": True, "has_tram": True, "has_bus": True, "has_bike_share": True,
        "is_walkable": True, "uber_available": True,
        "peak_season_months": [6, 7, 8], "shoulder_season_months": [4, 5, 9, 10],
        "off_season_months": [1, 2, 3, 11, 12],
        "safety_score": 0.80, "tourist_friendliness": 0.75, "english_proficiency": 0.45,
        "avg_daily_budget_budget": 55, "avg_daily_budget_midrange": 130, "avg_daily_budget_luxury": 350,
    },
    "bordeaux": {
        "latitude": 44.8378, "longitude": -0.5792, "timezone": "Europe/Paris",
        "country_code": "FR", "primary_language": "French", "currency_code": "EUR",
        "has_metro": False, "has_tram": True, "has_bus": True, "has_bike_share": True,
        "is_walkable": True, "uber_available": True,
        "peak_season_months": [6, 7, 8, 9], "shoulder_season_months": [4, 5, 10],
        "off_season_months": [1, 2, 3, 11, 12],
        "safety_score": 0.82, "tourist_friendliness": 0.78, "english_proficiency": 0.42,
        "avg_daily_budget_budget": 55, "avg_daily_budget_midrange": 130, "avg_daily_budget_luxury": 350,
    },
    # Spain
    "barcelona": {
        "latitude": 41.3874, "longitude": 2.1686, "timezone": "Europe/Madrid",
        "country_code": "ES", "primary_language": "Spanish", "secondary_languages": ["Catalan"],
        "currency_code": "EUR",
        "has_metro": True, "has_tram": True, "has_bus": True, "has_bike_share": True,
        "is_walkable": True, "uber_available": True,
        "peak_season_months": [6, 7, 8], "shoulder_season_months": [4, 5, 9, 10],
        "off_season_months": [1, 2, 3, 11, 12],
        "safety_score": 0.70, "tourist_friendliness": 0.85, "english_proficiency": 0.55,
        "avg_daily_budget_budget": 55, "avg_daily_budget_midrange": 140, "avg_daily_budget_luxury": 380,
    },
    "madrid": {
        "latitude": 40.4168, "longitude": -3.7038, "timezone": "Europe/Madrid",
        "country_code": "ES", "primary_language": "Spanish", "currency_code": "EUR",
        "has_metro": True, "has_tram": False, "has_bus": True, "has_bike_share": True,
        "is_walkable": True, "uber_available": True,
        "peak_season_months": [4, 5, 6, 9, 10], "shoulder_season_months": [3, 11],
        "off_season_months": [1, 2, 7, 8, 12],
        "safety_score": 0.78, "tourist_friendliness": 0.82, "english_proficiency": 0.50,
        "avg_daily_budget_budget": 50, "avg_daily_budget_midrange": 130, "avg_daily_budget_luxury": 350,
    },
    "seville": {
        "latitude": 37.3891, "longitude": -5.9845, "timezone": "Europe/Madrid",
        "country_code": "ES", "primary_language": "Spanish", "currency_code": "EUR",
        "has_metro": True, "has_tram": True, "has_bus": True, "has_bike_share": True,
        "is_walkable": True, "uber_available": True,
        "peak_season_months": [3, 4, 10, 11], "shoulder_season_months": [2, 5, 9, 12],
        "off_season_months": [1, 6, 7, 8],
        "safety_score": 0.80, "tourist_friendliness": 0.85, "english_proficiency": 0.40,
        "avg_daily_budget_budget": 45, "avg_daily_budget_midrange": 110, "avg_daily_budget_luxury": 300,
    },
    "granada": {
        "latitude": 37.1773, "longitude": -3.5986, "timezone": "Europe/Madrid",
        "country_code": "ES", "primary_language": "Spanish", "currency_code": "EUR",
        "has_metro": False, "has_tram": False, "has_bus": True, "has_bike_share": False,
        "is_walkable": True, "uber_available": False,
        "peak_season_months": [4, 5, 9, 10], "shoulder_season_months": [3, 6, 11],
        "off_season_months": [1, 2, 7, 8, 12],
        "safety_score": 0.82, "tourist_friendliness": 0.80, "english_proficiency": 0.38,
        "avg_daily_budget_budget": 40, "avg_daily_budget_midrange": 100, "avg_daily_budget_luxury": 280,
    },
    # Japan
    "tokyo": {
        "latitude": 35.6762, "longitude": 139.6503, "timezone": "Asia/Tokyo",
        "country_code": "JP", "primary_language": "Japanese", "currency_code": "JPY",
        "has_metro": True, "has_tram": False, "has_bus": True, "has_bike_share": True,
        "is_walkable": True, "uber_available": True,
        "peak_season_months": [3, 4, 10, 11], "shoulder_season_months": [5, 9],
        "off_season_months": [1, 2, 6, 7, 8, 12],
        "safety_score": 0.95, "tourist_friendliness": 0.85, "english_proficiency": 0.40,
        "avg_daily_budget_budget": 80, "avg_daily_budget_midrange": 180, "avg_daily_budget_luxury": 500,
    },
    "kyoto": {
        "latitude": 35.0116, "longitude": 135.7681, "timezone": "Asia/Tokyo",
        "country_code": "JP", "primary_language": "Japanese", "currency_code": "JPY",
        "has_metro": False, "has_tram": False, "has_bus": True, "has_bike_share": True,
        "is_walkable": True, "uber_available": False,
        "peak_season_months": [3, 4, 10, 11], "shoulder_season_months": [5, 9],
        "off_season_months": [1, 2, 6, 7, 8, 12],
        "safety_score": 0.95, "tourist_friendliness": 0.88, "english_proficiency": 0.35,
        "avg_daily_budget_budget": 70, "avg_daily_budget_midrange": 160, "avg_daily_budget_luxury": 450,
    },
    "osaka": {
        "latitude": 34.6937, "longitude": 135.5023, "timezone": "Asia/Tokyo",
        "country_code": "JP", "primary_language": "Japanese", "currency_code": "JPY",
        "has_metro": True, "has_tram": False, "has_bus": True, "has_bike_share": True,
        "is_walkable": True, "uber_available": True,
        "peak_season_months": [3, 4, 10, 11], "shoulder_season_months": [5, 9],
        "off_season_months": [1, 2, 6, 7, 8, 12],
        "safety_score": 0.93, "tourist_friendliness": 0.85, "english_proficiency": 0.35,
        "avg_daily_budget_budget": 65, "avg_daily_budget_midrange": 150, "avg_daily_budget_luxury": 400,
    },
    "hiroshima": {
        "latitude": 34.3853, "longitude": 132.4553, "timezone": "Asia/Tokyo",
        "country_code": "JP", "primary_language": "Japanese", "currency_code": "JPY",
        "has_metro": False, "has_tram": True, "has_bus": True, "has_bike_share": True,
        "is_walkable": True, "uber_available": False,
        "peak_season_months": [3, 4, 10, 11], "shoulder_season_months": [5, 9],
        "off_season_months": [1, 2, 6, 7, 8, 12],
        "safety_score": 0.95, "tourist_friendliness": 0.90, "english_proficiency": 0.30,
        "avg_daily_budget_budget": 55, "avg_daily_budget_midrange": 120, "avg_daily_budget_luxury": 350,
    },
    # UK
    "london": {
        "latitude": 51.5074, "longitude": -0.1278, "timezone": "Europe/London",
        "country_code": "GB", "primary_language": "English", "currency_code": "GBP",
        "has_metro": True, "has_tram": False, "has_bus": True, "has_bike_share": True,
        "is_walkable": True, "uber_available": True,
        "peak_season_months": [6, 7, 8], "shoulder_season_months": [4, 5, 9, 10],
        "off_season_months": [1, 2, 3, 11, 12],
        "safety_score": 0.75, "tourist_friendliness": 0.88, "english_proficiency": 1.00,
        "avg_daily_budget_budget": 80, "avg_daily_budget_midrange": 200, "avg_daily_budget_luxury": 550,
    },
    "edinburgh": {
        "latitude": 55.9533, "longitude": -3.1883, "timezone": "Europe/London",
        "country_code": "GB", "primary_language": "English", "currency_code": "GBP",
        "has_metro": False, "has_tram": True, "has_bus": True, "has_bike_share": True,
        "is_walkable": True, "uber_available": True,
        "peak_season_months": [7, 8], "shoulder_season_months": [5, 6, 9],
        "off_season_months": [1, 2, 3, 4, 10, 11, 12],
        "safety_score": 0.85, "tourist_friendliness": 0.90, "english_proficiency": 1.00,
        "avg_daily_budget_budget": 60, "avg_daily_budget_midrange": 150, "avg_daily_budget_luxury": 400,
    },
}

# Neighborhood data for key cities
NEIGHBORHOODS: Dict[str, List[Dict[str, Any]]] = {
    "rome": [
        {"name": "Centro Storico", "local_name": "Centro Storico", "latitude": 41.8986, "longitude": 12.4769,
         "vibe_tags": ["historical", "cultural", "romantic"], "description": "The ancient heart of Rome with the Pantheon, Piazza Navona, and countless trattorias.",
         "safety_day": 0.80, "safety_night": 0.65, "walkability_score": 0.95, "transit_accessibility": 0.80,
         "best_for": ["couple", "solo", "cultural"], "best_time_of_day": "morning"},
        {"name": "Trastevere", "local_name": "Trastevere", "latitude": 41.8864, "longitude": 12.4699,
         "vibe_tags": ["foodie", "nightlife", "local", "romantic"], "description": "Charming cobblestone neighborhood known for authentic Roman cuisine and vibrant nightlife.",
         "safety_day": 0.82, "safety_night": 0.70, "walkability_score": 0.90, "transit_accessibility": 0.70,
         "best_for": ["couple", "friends", "foodie"], "best_time_of_day": "evening"},
        {"name": "Monti", "local_name": "Monti", "latitude": 41.8954, "longitude": 12.4942,
         "vibe_tags": ["trendy", "shopping", "local", "artsy"], "description": "Rome's hippest neighborhood with vintage shops, craft cocktail bars, and art galleries.",
         "safety_day": 0.85, "safety_night": 0.72, "walkability_score": 0.88, "transit_accessibility": 0.85,
         "best_for": ["solo", "friends", "shopping"], "best_time_of_day": "afternoon"},
        {"name": "Vatican / Prati", "local_name": "Prati", "latitude": 41.9073, "longitude": 12.4534,
         "vibe_tags": ["cultural", "historical", "family"], "description": "Home to Vatican City, St. Peter's Basilica, and upscale dining along Via Cola di Rienzo.",
         "safety_day": 0.88, "safety_night": 0.78, "walkability_score": 0.85, "transit_accessibility": 0.82,
         "best_for": ["family", "cultural", "couple"], "best_time_of_day": "morning"},
    ],
    "paris": [
        {"name": "Le Marais", "local_name": "Le Marais", "latitude": 48.8566, "longitude": 2.3622,
         "vibe_tags": ["trendy", "cultural", "shopping", "foodie"], "description": "Historic and fashionable district with museums, boutiques, and excellent falafel.",
         "safety_day": 0.82, "safety_night": 0.70, "walkability_score": 0.95, "transit_accessibility": 0.90,
         "best_for": ["couple", "solo", "friends", "shopping"], "best_time_of_day": "afternoon"},
        {"name": "Montmartre", "local_name": "Montmartre", "latitude": 48.8867, "longitude": 2.3431,
         "vibe_tags": ["romantic", "artsy", "photography", "cultural"], "description": "Hilltop artist village crowned by Sacre-Coeur with panoramic views, street painters, and cozy cafes.",
         "safety_day": 0.75, "safety_night": 0.55, "walkability_score": 0.75, "transit_accessibility": 0.80,
         "best_for": ["couple", "photography", "solo"], "best_time_of_day": "morning"},
        {"name": "Saint-Germain-des-Pres", "local_name": "Saint-Germain-des-Pres", "latitude": 48.8539, "longitude": 2.3338,
         "vibe_tags": ["cultural", "foodie", "romantic", "literary"], "description": "Intellectual Left Bank neighborhood with legendary cafes, bookshops, and galleries.",
         "safety_day": 0.88, "safety_night": 0.78, "walkability_score": 0.92, "transit_accessibility": 0.88,
         "best_for": ["couple", "solo", "cultural"], "best_time_of_day": "afternoon"},
        {"name": "Latin Quarter", "local_name": "Quartier Latin", "latitude": 48.8497, "longitude": 2.3471,
         "vibe_tags": ["cultural", "student", "foodie", "historical"], "description": "Historic student quarter around the Sorbonne with affordable eats and Shakespeare & Company.",
         "safety_day": 0.80, "safety_night": 0.68, "walkability_score": 0.90, "transit_accessibility": 0.88,
         "best_for": ["solo", "friends", "budget"], "best_time_of_day": "evening"},
    ],
    "florence": [
        {"name": "Centro / Duomo", "local_name": "Centro", "latitude": 43.7731, "longitude": 11.2560,
         "vibe_tags": ["cultural", "historical", "art", "photography"], "description": "The historic core around the Cathedral, Uffizi, and Ponte Vecchio.",
         "safety_day": 0.85, "safety_night": 0.70, "walkability_score": 0.95, "transit_accessibility": 0.75,
         "best_for": ["couple", "solo", "cultural"], "best_time_of_day": "morning"},
        {"name": "Oltrarno", "local_name": "Oltrarno", "latitude": 43.7657, "longitude": 11.2482,
         "vibe_tags": ["artisan", "local", "foodie", "bohemian"], "description": "Artisan quarter south of the Arno with workshops, Palazzo Pitti, and authentic trattorias.",
         "safety_day": 0.82, "safety_night": 0.68, "walkability_score": 0.88, "transit_accessibility": 0.70,
         "best_for": ["solo", "couple", "foodie"], "best_time_of_day": "afternoon"},
    ],
    "barcelona": [
        {"name": "Gothic Quarter", "local_name": "Barri Gotic", "latitude": 41.3833, "longitude": 2.1761,
         "vibe_tags": ["historical", "cultural", "nightlife", "shopping"], "description": "Medieval heart of Barcelona with narrow alleys, the Cathedral, and vibrant plazas.",
         "safety_day": 0.72, "safety_night": 0.55, "walkability_score": 0.92, "transit_accessibility": 0.88,
         "best_for": ["couple", "friends", "cultural"], "best_time_of_day": "morning"},
        {"name": "El Born", "local_name": "El Born", "latitude": 41.3850, "longitude": 2.1830,
         "vibe_tags": ["trendy", "foodie", "nightlife", "artsy"], "description": "Hip neighborhood with Picasso Museum, boutiques, cocktail bars, and the market.",
         "safety_day": 0.78, "safety_night": 0.62, "walkability_score": 0.90, "transit_accessibility": 0.85,
         "best_for": ["friends", "couple", "solo"], "best_time_of_day": "evening"},
    ],
    "tokyo": [
        {"name": "Shibuya", "local_name": "渋谷", "latitude": 35.6580, "longitude": 139.7016,
         "vibe_tags": ["modern", "shopping", "nightlife", "iconic"], "description": "Famous crossing, fashion, and entertainment hub of Tokyo.",
         "safety_day": 0.92, "safety_night": 0.85, "walkability_score": 0.88, "transit_accessibility": 0.95,
         "best_for": ["friends", "solo", "shopping"], "best_time_of_day": "evening"},
        {"name": "Asakusa", "local_name": "浅草", "latitude": 35.7148, "longitude": 139.7967,
         "vibe_tags": ["traditional", "cultural", "historical", "foodie"], "description": "Old Tokyo with Senso-ji temple, traditional shops, and street food.",
         "safety_day": 0.95, "safety_night": 0.88, "walkability_score": 0.92, "transit_accessibility": 0.88,
         "best_for": ["family", "cultural", "solo"], "best_time_of_day": "morning"},
    ],
    "london": [
        {"name": "Westminster", "local_name": "Westminster", "latitude": 51.4975, "longitude": -0.1357,
         "vibe_tags": ["historical", "cultural", "iconic", "photography"], "description": "Political and tourist heart with Big Ben, Westminster Abbey, and Buckingham Palace.",
         "safety_day": 0.85, "safety_night": 0.75, "walkability_score": 0.90, "transit_accessibility": 0.95,
         "best_for": ["family", "couple", "cultural"], "best_time_of_day": "morning"},
        {"name": "South Bank", "local_name": "South Bank", "latitude": 51.5055, "longitude": -0.1150,
         "vibe_tags": ["cultural", "artsy", "foodie", "photography"], "description": "Cultural strip along the Thames with Tate Modern, Borough Market, and the Globe.",
         "safety_day": 0.82, "safety_night": 0.72, "walkability_score": 0.92, "transit_accessibility": 0.88,
         "best_for": ["couple", "friends", "solo", "foodie"], "best_time_of_day": "afternoon"},
    ],
    "kyoto": [
        {"name": "Higashiyama", "local_name": "東山", "latitude": 34.9990, "longitude": 135.7852,
         "vibe_tags": ["traditional", "cultural", "photography", "peaceful"], "description": "Atmospheric district with temples, tea houses, and geisha sightings.",
         "safety_day": 0.95, "safety_night": 0.88, "walkability_score": 0.85, "transit_accessibility": 0.75,
         "best_for": ["couple", "solo", "photography"], "best_time_of_day": "morning"},
    ],
}


async def seed_cities(db: AsyncSession) -> Dict[str, City]:
    """Seed all cities from COUNTRY_DATABASE with enriched metadata."""
    city_map = {}

    for country_id, country_data in COUNTRY_DATABASE.items():
        country_name = country_data["name"]
        for city_key, city_data in country_data["cities"].items():
            # Check if city already exists
            stmt = select(City).where(City.name == city_data["name"], City.country == country_name)
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                logger.info(f"  Skipping existing city: {city_data['name']}")
                city_map[city_key] = existing
                continue

            meta = CITY_METADATA.get(city_key, {})

            city = City(
                id=uuid4(),
                name=city_data["name"],
                country=country_name,
                country_code=meta.get("country_code"),
                latitude=meta.get("latitude"),
                longitude=meta.get("longitude"),
                timezone=meta.get("timezone"),
                primary_language=meta.get("primary_language", country_data.get("languages", [""])[0]),
                secondary_languages=meta.get("secondary_languages"),
                currency_code=meta.get("currency_code", country_data.get("currency")),
                avg_daily_budget_budget=meta.get("avg_daily_budget_budget"),
                avg_daily_budget_midrange=meta.get("avg_daily_budget_midrange"),
                avg_daily_budget_luxury=meta.get("avg_daily_budget_luxury"),
                has_metro=meta.get("has_metro", False),
                has_tram=meta.get("has_tram", False),
                has_bus=meta.get("has_bus", True),
                has_bike_share=meta.get("has_bike_share", False),
                is_walkable=meta.get("is_walkable", True),
                uber_available=meta.get("uber_available", False),
                peak_season_months=meta.get("peak_season_months"),
                shoulder_season_months=meta.get("shoulder_season_months"),
                off_season_months=meta.get("off_season_months"),
                safety_score=meta.get("safety_score"),
                tourist_friendliness=meta.get("tourist_friendliness"),
                english_proficiency=meta.get("english_proficiency"),
            )

            db.add(city)
            city_map[city_key] = city
            logger.info(f"  Added city: {city_data['name']}, {country_name}")

    await db.flush()
    return city_map


async def seed_neighborhoods(db: AsyncSession, city_map: Dict[str, City]) -> int:
    """Seed neighborhoods for cities that have data."""
    count = 0

    for city_key, neighborhoods in NEIGHBORHOODS.items():
        city = city_map.get(city_key)
        if not city:
            logger.warning(f"  City not found for neighborhoods: {city_key}")
            continue

        for n_data in neighborhoods:
            # Check if neighborhood already exists
            stmt = select(Neighborhood).where(
                Neighborhood.city_id == city.id,
                Neighborhood.name == n_data["name"],
            )
            result = await db.execute(stmt)
            if result.scalar_one_or_none():
                logger.info(f"  Skipping existing neighborhood: {n_data['name']}")
                continue

            neighborhood = Neighborhood(
                id=uuid4(),
                city_id=city.id,
                name=n_data["name"],
                local_name=n_data.get("local_name"),
                latitude=n_data.get("latitude"),
                longitude=n_data.get("longitude"),
                vibe_tags=n_data.get("vibe_tags"),
                description=n_data.get("description"),
                safety_day=n_data.get("safety_day"),
                safety_night=n_data.get("safety_night"),
                walkability_score=n_data.get("walkability_score"),
                transit_accessibility=n_data.get("transit_accessibility"),
                best_for=n_data.get("best_for"),
                best_time_of_day=n_data.get("best_time_of_day"),
            )

            db.add(neighborhood)
            count += 1
            logger.info(f"  Added neighborhood: {n_data['name']} ({city_key})")

    await db.flush()
    return count


async def create_proximity_relationships(db: AsyncSession, city_map: Dict[str, City]) -> int:
    """Auto-create NEAR_TO relationships for cities with POIs."""
    builder = RelationshipBuilder(db)
    total = 0

    for city_key, city in city_map.items():
        logger.info(f"  Creating proximity relationships for {city.name}...")
        try:
            count = await builder.auto_create_proximity_relationships(
                city=city.name,
                max_distance_km=0.5,
            )
            total += count
            logger.info(f"  Created {count} relationships for {city.name}")
        except Exception as e:
            logger.warning(f"  Error creating relationships for {city.name}: {e}")

    return total


async def main():
    """Main function to seed all KG data."""
    logger.info("=" * 60)
    logger.info("SEEDING KNOWLEDGE GRAPH DATA")
    logger.info("=" * 60)

    async with AsyncSessionLocal() as db:
        # 1. Seed cities
        logger.info("\n--- Seeding Cities ---")
        city_map = await seed_cities(db)
        logger.info(f"Cities in map: {len(city_map)}")

        # 2. Seed neighborhoods
        logger.info("\n--- Seeding Neighborhoods ---")
        n_count = await seed_neighborhoods(db, city_map)
        logger.info(f"Added {n_count} neighborhoods")

        # 3. Create proximity relationships
        logger.info("\n--- Creating POI Proximity Relationships ---")
        r_count = await create_proximity_relationships(db, city_map)
        logger.info(f"Created {r_count} POI relationships")

        # Commit all changes
        await db.commit()

    logger.info("\n" + "=" * 60)
    logger.info("KNOWLEDGE GRAPH SEEDING COMPLETE!")
    logger.info(f"  Cities: {len(city_map)}")
    logger.info(f"  Neighborhoods: {n_count}")
    logger.info(f"  POI Relationships: {r_count}")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
