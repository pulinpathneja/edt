from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://edt_user:edt_password@localhost:5432/edt_db"
    database_url_sync: str = "postgresql+psycopg2://edt_user:edt_password@localhost:5432/edt_db"

    # Embedding model
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    embedding_dimension: int = 384

    # Optional APIs
    google_places_api_key: str = ""
    google_search_api_key: str = ""
    google_search_cx: str = ""

    # Application
    app_name: str = "EDT Itinerary System"
    debug: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


# Pacing configuration
PACING_CONFIG = {
    "slow": {
        "anchors_per_day": 1,
        "max_activities": 3,
        "min_buffer_minutes": 60,
        "meal_duration_minutes": 90,
        "must_include_breaks": True,
        "break_after_heavy_minutes": 60,
        "break_after_moderate_minutes": 30,
    },
    "moderate": {
        "anchors_per_day": 2,
        "max_activities": 5,
        "min_buffer_minutes": 30,
        "meal_duration_minutes": 60,
        "must_include_breaks": True,
        "break_after_heavy_minutes": 45,
        "break_after_moderate_minutes": 15,
    },
    "fast": {
        "anchors_per_day": 3,
        "max_activities": 7,
        "min_buffer_minutes": 15,
        "meal_duration_minutes": 45,
        "must_include_breaks": False,
        "break_after_heavy_minutes": 20,
        "break_after_moderate_minutes": 0,
    },
}

# Scoring configuration
SCORING_CONFIG = {
    "must_see_boost": 0.15,  # Boost for is_must_see attractions
    "iconic_guarantee": True,  # Ensure at least 1 must-see per day
}

# Persona-based duration multipliers
# Adjusts typical_duration_minutes based on traveler type
PERSONA_DURATION_MULTIPLIERS = {
    "family": {
        "museum": 0.5,         # Kids get bored quickly
        "historical": 0.6,
        "park": 1.2,           # Kids love parks
        "market": 0.8,
        "walking_tour": 0.6,   # Shorter attention span
        "default": 0.7,
    },
    "honeymoon": {
        "museum": 0.5,         # Not here for deep history
        "historical": 0.6,
        "park": 1.0,
        "viewpoint": 1.2,      # Romantic photo spots
        "trattoria": 1.3,      # Long romantic dinners
        "fine_dining": 1.4,
        "cocktail_bar": 1.2,
        "default": 0.8,
    },
    "couple": {
        "museum": 0.8,
        "historical": 0.8,
        "viewpoint": 1.1,
        "default": 0.9,
    },
    "solo": {
        "museum": 1.2,         # Can take their time
        "historical": 1.2,
        "walking_tour": 1.0,
        "market": 1.1,         # Explore freely
        "default": 1.0,
    },
    "friends": {
        "museum": 0.7,         # Quick highlights
        "historical": 0.7,
        "nightlife": 1.5,      # Party longer
        "cocktail_bar": 1.3,
        "market": 1.0,
        "walking_tour": 0.8,
        "default": 0.8,
    },
    "seniors": {
        "museum": 0.9,         # Need rests but interested
        "historical": 0.8,
        "park": 1.3,           # Enjoy slow walks
        "walking_tour": 0.6,   # Tiring
        "trattoria": 1.2,      # Long leisurely meals
        "default": 0.8,
    },
    "kids": {
        "museum": 0.4,
        "historical": 0.4,
        "park": 1.5,
        "dessert": 1.2,
        "default": 0.6,
    },
    "business": {
        "museum": 0.6,
        "historical": 0.6,
        "fine_dining": 1.2,
        "default": 0.7,
    },
}

# Break rules based on activity intensity
BREAK_RULES = {
    "heavy_subcategories": ["museum", "historical"],
    "heavy_min_duration": 90,
    "default_break_type": {
        "heavy": "coffee_gelato",
        "moderate": "rest",
    },
}

# Group types
GROUP_TYPES = [
    "family",
    "kids",
    "couple",
    "honeymoon",
    "solo",
    "friends",
    "seniors",
    "business",
]

# Vibe categories
VIBE_CATEGORIES = [
    "adventure",
    "relaxation",
    "cultural",
    "foodie",
    "nightlife",
    "nature",
    "shopping",
    "photography",
    "wellness",
    "romantic",
]

# POI categories
POI_CATEGORIES = [
    "attraction",
    "restaurant",
    "activity",
    "accommodation",
    "shopping",
    "nightlife",
    "transportation",
]

# Time of day options
TIME_OF_DAY = ["morning", "afternoon", "evening", "night", "any"]

# Seasons
SEASONS = ["spring", "summer", "fall", "winter", "all"]
