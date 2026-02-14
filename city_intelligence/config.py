"""
Configuration for City Intelligence System
"""
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class CityIntelConfig:
    # Reddit API
    reddit_client_id: str = os.getenv("REDDIT_CLIENT_ID", "")
    reddit_client_secret: str = os.getenv("REDDIT_CLIENT_SECRET", "")
    reddit_user_agent: str = os.getenv("REDDIT_USER_AGENT", "CityIntelBot/1.0")

    # Viator API
    viator_api_key: str = os.getenv("VIATOR_API_KEY", "")

    # GetYourGuide API
    gyg_partner_id: str = os.getenv("GYG_PARTNER_ID", "")
    gyg_api_key: str = os.getenv("GYG_API_KEY", "")

    # Eventbrite API
    eventbrite_token: str = os.getenv("EVENTBRITE_TOKEN", "")

    # Output settings
    output_dir: str = os.getenv("CITY_INTEL_OUTPUT_DIR", "city_intelligence/cities")

    # Search settings
    reddit_post_limit: int = 100
    min_upvotes: int = 50
    min_comments: int = 10
    max_post_age_days: int = 730  # 2 years


# Subreddit patterns for cities
CITY_SUBREDDIT_PATTERNS = [
    "{city}",           # r/toronto
    "Ask{city}",        # r/AskNYC
    "{city}food",       # r/FoodNYC
    "visit{city}",      # r/visitseattle
]

# General travel subreddits
TRAVEL_SUBREDDITS = [
    "travel",
    "solotravel",
    "shoestring",
    "TravelHacks",
    "backpacking",
]

# Search categories
SEARCH_CATEGORIES = {
    "general": [
        "things to do",
        "must see",
        "hidden gems",
        "local tips",
        "honest review",
    ],
    "challenges": [
        "problems",
        "avoid",
        "scams",
        "safety",
        "overrated",
    ],
    "pros_cons": [
        "pros cons",
        "worth visiting",
        "underrated",
        "best worst",
    ],
    "family_friendly": [
        "with kids",
        "family friendly",
        "stroller",
        "playground",
        "children",
    ],
    "food": [
        "best food",
        "where locals eat",
        "street food",
        "cheap eats",
        "food market",
    ],
    "neighborhoods": [
        "best neighborhood",
        "walkable",
        "where to stay",
        "areas",
    ],
    "budget": [
        "budget",
        "cheap",
        "free things",
        "affordable",
    ],
    "nightlife": [
        "nightlife",
        "bars",
        "clubs",
        "night out",
    ],
}

# Personas for filtering recommendations
PERSONAS = {
    "solo_traveler": {
        "keywords": ["solo", "alone", "single traveler", "backpacker"],
        "interests": ["safety", "hostels", "social", "meetup"],
    },
    "couple": {
        "keywords": ["couple", "romantic", "honeymoon", "date"],
        "interests": ["romantic", "scenic", "intimate", "luxury"],
    },
    "family": {
        "keywords": ["family", "kids", "children", "toddler", "baby"],
        "interests": ["kid-friendly", "parks", "activities", "safe"],
    },
    "budget": {
        "keywords": ["budget", "cheap", "backpacker", "shoestring"],
        "interests": ["free", "affordable", "hostel", "street food"],
    },
    "luxury": {
        "keywords": ["luxury", "upscale", "high-end", "boutique"],
        "interests": ["fine dining", "spa", "5-star", "exclusive"],
    },
    "adventure": {
        "keywords": ["adventure", "outdoor", "hiking", "extreme"],
        "interests": ["hiking", "sports", "nature", "adrenaline"],
    },
    "foodie": {
        "keywords": ["food", "culinary", "gastronomy", "eating"],
        "interests": ["restaurants", "markets", "cooking class", "local cuisine"],
    },
    "culture": {
        "keywords": ["culture", "history", "art", "museum"],
        "interests": ["museums", "architecture", "heritage", "tours"],
    },
}
