"""
Shared country database for multi-city itinerary planning.
Used by both the backend API and the notebook.
"""
from typing import Dict, List, Optional, Tuple


CITY_BBOXES: Dict[str, Dict] = {
    # Italy
    "rome": {"min_lon": 12.40, "min_lat": 41.85, "max_lon": 12.55, "max_lat": 41.95, "country": "Italy"},
    "florence": {"min_lon": 11.20, "min_lat": 43.74, "max_lon": 11.30, "max_lat": 43.80, "country": "Italy"},
    "venice": {"min_lon": 12.30, "min_lat": 45.41, "max_lon": 12.37, "max_lat": 45.46, "country": "Italy"},
    "milan": {"min_lon": 9.10, "min_lat": 45.43, "max_lon": 9.23, "max_lat": 45.50, "country": "Italy"},
    "naples": {"min_lon": 14.20, "min_lat": 40.82, "max_lon": 14.30, "max_lat": 40.87, "country": "Italy"},
    "amalfi": {"min_lon": 14.55, "min_lat": 40.62, "max_lon": 14.65, "max_lat": 40.66, "country": "Italy"},
    # France
    "paris": {"min_lon": 2.25, "min_lat": 48.81, "max_lon": 2.42, "max_lat": 48.91, "country": "France"},
    "nice": {"min_lon": 7.20, "min_lat": 43.68, "max_lon": 7.30, "max_lat": 43.74, "country": "France"},
    "lyon": {"min_lon": 4.79, "min_lat": 45.72, "max_lon": 4.88, "max_lat": 45.79, "country": "France"},
    "bordeaux": {"min_lon": -0.63, "min_lat": 44.81, "max_lon": -0.53, "max_lat": 44.87, "country": "France"},
    # Spain
    "barcelona": {"min_lon": 2.05, "min_lat": 41.32, "max_lon": 2.23, "max_lat": 41.47, "country": "Spain"},
    "madrid": {"min_lon": -3.75, "min_lat": 40.38, "max_lon": -3.65, "max_lat": 40.46, "country": "Spain"},
    "seville": {"min_lon": -6.01, "min_lat": 37.35, "max_lon": -5.93, "max_lat": 37.41, "country": "Spain"},
    "granada": {"min_lon": -3.62, "min_lat": 37.15, "max_lon": -3.57, "max_lat": 37.20, "country": "Spain"},
    # Japan
    "tokyo": {"min_lon": 139.55, "min_lat": 35.55, "max_lon": 139.85, "max_lat": 35.80, "country": "Japan"},
    "kyoto": {"min_lon": 135.70, "min_lat": 34.95, "max_lon": 135.80, "max_lat": 35.05, "country": "Japan"},
    "osaka": {"min_lon": 135.40, "min_lat": 34.60, "max_lon": 135.55, "max_lat": 34.72, "country": "Japan"},
    "hiroshima": {"min_lon": 132.42, "min_lat": 34.36, "max_lon": 132.48, "max_lat": 34.42, "country": "Japan"},
    # UK
    "london": {"min_lon": -0.20, "min_lat": 51.45, "max_lon": 0.05, "max_lat": 51.55, "country": "UK"},
    "edinburgh": {"min_lon": -3.25, "min_lat": 55.92, "max_lon": -3.15, "max_lat": 55.97, "country": "UK"},
    "bath": {"min_lon": -2.40, "min_lat": 51.37, "max_lon": -2.33, "max_lat": 51.40, "country": "UK"},
    "oxford": {"min_lon": -1.28, "min_lat": 51.73, "max_lon": -1.23, "max_lat": 51.77, "country": "UK"},
}


COUNTRY_DATABASE: Dict[str, Dict] = {
    "italy": {
        "name": "Italy",
        "flag": "🇮🇹",
        "currency": "EUR",
        "languages": ["Italian"],
        "cities": {
            "rome": {
                "name": "Rome",
                "min_days": 2,
                "max_days": 5,
                "ideal_days": 3,
                "priority": 1,
                "highlights": ["Colosseum", "Vatican", "Trevi Fountain", "Roman Forum"],
                "vibes": ["cultural", "historical", "foodie", "romantic"],
                "best_for": ["couple", "solo", "family", "friends"],
            },
            "florence": {
                "name": "Florence",
                "min_days": 2,
                "max_days": 4,
                "ideal_days": 2,
                "priority": 2,
                "highlights": ["Uffizi Gallery", "Duomo", "Ponte Vecchio", "Accademia"],
                "vibes": ["art", "cultural", "romantic", "foodie"],
                "best_for": ["couple", "solo", "honeymoon"],
            },
            "venice": {
                "name": "Venice",
                "min_days": 1,
                "max_days": 3,
                "ideal_days": 2,
                "priority": 2,
                "highlights": ["St. Mark's Square", "Grand Canal", "Rialto Bridge", "Murano"],
                "vibes": ["romantic", "cultural", "photography", "unique"],
                "best_for": ["couple", "honeymoon", "solo", "photography"],
            },
            "milan": {
                "name": "Milan",
                "min_days": 1,
                "max_days": 3,
                "ideal_days": 2,
                "priority": 3,
                "highlights": ["Duomo di Milano", "Last Supper", "Galleria", "Fashion District"],
                "vibes": ["shopping", "art", "modern", "foodie"],
                "best_for": ["friends", "solo", "couple", "business"],
            },
            "naples": {
                "name": "Naples",
                "min_days": 1,
                "max_days": 3,
                "ideal_days": 2,
                "priority": 3,
                "highlights": ["Pompeii", "Pizza", "Naples Underground", "Spaccanapoli"],
                "vibes": ["foodie", "historical", "adventure", "local"],
                "best_for": ["foodie", "friends", "solo", "adventure"],
            },
            "amalfi": {
                "name": "Amalfi Coast",
                "min_days": 1,
                "max_days": 3,
                "ideal_days": 2,
                "priority": 3,
                "highlights": ["Positano", "Ravello", "Path of the Gods", "Coastal Views"],
                "vibes": ["romantic", "relaxation", "photography", "nature"],
                "best_for": ["couple", "honeymoon", "relaxation"],
            },
        },
        "travel_times": {
            ("rome", "florence"): 95,
            ("rome", "venice"): 225,
            ("rome", "milan"): 180,
            ("rome", "naples"): 70,
            ("florence", "venice"): 125,
            ("florence", "milan"): 100,
            ("venice", "milan"): 150,
            ("naples", "amalfi"): 75,
            ("rome", "amalfi"): 165,
        },
        "popular_routes": [
            ["rome", "florence"],
            ["rome", "florence", "venice"],
            ["rome", "naples", "amalfi"],
            ["milan", "florence", "rome"],
            ["rome", "florence", "venice", "milan"],
        ],
    },
    "france": {
        "name": "France",
        "flag": "🇫🇷",
        "currency": "EUR",
        "languages": ["French"],
        "cities": {
            "paris": {
                "name": "Paris",
                "min_days": 2,
                "max_days": 6,
                "ideal_days": 4,
                "priority": 1,
                "highlights": ["Eiffel Tower", "Louvre", "Notre-Dame", "Montmartre"],
                "vibes": ["romantic", "cultural", "foodie", "art"],
                "best_for": ["couple", "honeymoon", "solo", "family"],
            },
            "nice": {
                "name": "Nice",
                "min_days": 2,
                "max_days": 4,
                "ideal_days": 2,
                "priority": 2,
                "highlights": ["Promenade des Anglais", "Old Town", "Castle Hill", "Beach"],
                "vibes": ["beach", "relaxation", "foodie", "photography"],
                "best_for": ["couple", "solo", "relaxation", "family"],
            },
            "lyon": {
                "name": "Lyon",
                "min_days": 1,
                "max_days": 3,
                "ideal_days": 2,
                "priority": 3,
                "highlights": ["Old Lyon", "Basilica", "Food Market", "Traboules"],
                "vibes": ["foodie", "cultural", "local"],
                "best_for": ["foodie", "couple", "solo"],
            },
            "bordeaux": {
                "name": "Bordeaux",
                "min_days": 2,
                "max_days": 3,
                "ideal_days": 2,
                "priority": 3,
                "highlights": ["Wine Regions", "Old Town", "La Cité du Vin"],
                "vibes": ["wine", "foodie", "relaxation", "cultural"],
                "best_for": ["couple", "foodie", "wine lovers"],
            },
        },
        "travel_times": {
            ("paris", "nice"): 330,
            ("paris", "lyon"): 120,
            ("paris", "bordeaux"): 140,
            ("lyon", "nice"): 280,
        },
        "popular_routes": [
            ["paris", "nice"],
            ["paris", "lyon", "nice"],
            ["paris", "bordeaux"],
        ],
    },
    "spain": {
        "name": "Spain",
        "flag": "🇪🇸",
        "currency": "EUR",
        "languages": ["Spanish"],
        "cities": {
            "barcelona": {
                "name": "Barcelona",
                "min_days": 2,
                "max_days": 5,
                "ideal_days": 3,
                "priority": 1,
                "highlights": ["Sagrada Familia", "Park Güell", "Gothic Quarter", "La Rambla"],
                "vibes": ["cultural", "beach", "nightlife", "art"],
                "best_for": ["couple", "friends", "family", "solo"],
            },
            "madrid": {
                "name": "Madrid",
                "min_days": 2,
                "max_days": 4,
                "ideal_days": 2,
                "priority": 2,
                "highlights": ["Prado Museum", "Royal Palace", "Retiro Park", "Plaza Mayor"],
                "vibes": ["cultural", "nightlife", "foodie", "art"],
                "best_for": ["couple", "friends", "solo"],
            },
            "seville": {
                "name": "Seville",
                "min_days": 2,
                "max_days": 3,
                "ideal_days": 2,
                "priority": 3,
                "highlights": ["Alcázar", "Cathedral", "Flamenco", "Plaza de España"],
                "vibes": ["cultural", "romantic", "foodie", "flamenco"],
                "best_for": ["couple", "solo", "cultural"],
            },
            "granada": {
                "name": "Granada",
                "min_days": 1,
                "max_days": 2,
                "ideal_days": 2,
                "priority": 3,
                "highlights": ["Alhambra", "Albaicín", "Tapas Culture"],
                "vibes": ["cultural", "historical", "foodie"],
                "best_for": ["couple", "solo", "history lovers"],
            },
        },
        "travel_times": {
            ("barcelona", "madrid"): 150,
            ("madrid", "seville"): 150,
            ("seville", "granada"): 180,
            ("barcelona", "seville"): 330,
        },
        "popular_routes": [
            ["barcelona", "madrid"],
            ["barcelona", "madrid", "seville"],
            ["madrid", "seville", "granada"],
        ],
    },
    "japan": {
        "name": "Japan",
        "flag": "🇯🇵",
        "currency": "JPY",
        "languages": ["Japanese"],
        "cities": {
            "tokyo": {
                "name": "Tokyo",
                "min_days": 3,
                "max_days": 6,
                "ideal_days": 4,
                "priority": 1,
                "highlights": ["Shibuya", "Senso-ji", "Meiji Shrine", "Akihabara"],
                "vibes": ["modern", "cultural", "foodie", "shopping"],
                "best_for": ["family", "couple", "solo", "friends"],
            },
            "kyoto": {
                "name": "Kyoto",
                "min_days": 2,
                "max_days": 4,
                "ideal_days": 3,
                "priority": 2,
                "highlights": ["Fushimi Inari", "Kinkaku-ji", "Arashiyama", "Geisha District"],
                "vibes": ["traditional", "cultural", "peaceful", "photography"],
                "best_for": ["couple", "solo", "seniors", "cultural"],
            },
            "osaka": {
                "name": "Osaka",
                "min_days": 1,
                "max_days": 3,
                "ideal_days": 2,
                "priority": 3,
                "highlights": ["Dotonbori", "Osaka Castle", "Street Food", "Universal Studios"],
                "vibes": ["foodie", "nightlife", "fun", "local"],
                "best_for": ["friends", "family", "foodie"],
            },
            "hiroshima": {
                "name": "Hiroshima",
                "min_days": 1,
                "max_days": 2,
                "ideal_days": 1,
                "priority": 4,
                "highlights": ["Peace Memorial", "Miyajima Island", "Atomic Bomb Dome"],
                "vibes": ["historical", "peaceful", "cultural"],
                "best_for": ["solo", "couple", "history lovers"],
            },
        },
        "travel_times": {
            ("tokyo", "kyoto"): 135,
            ("tokyo", "osaka"): 150,
            ("kyoto", "osaka"): 15,
            ("osaka", "hiroshima"): 90,
            ("kyoto", "hiroshima"): 100,
        },
        "popular_routes": [
            ["tokyo", "kyoto"],
            ["tokyo", "kyoto", "osaka"],
            ["tokyo", "kyoto", "osaka", "hiroshima"],
        ],
    },
    "uk": {
        "name": "United Kingdom",
        "flag": "🇬🇧",
        "currency": "GBP",
        "languages": ["English"],
        "cities": {
            "london": {
                "name": "London",
                "min_days": 2,
                "max_days": 6,
                "ideal_days": 4,
                "priority": 1,
                "highlights": ["Big Ben", "Tower of London", "British Museum", "Buckingham Palace"],
                "vibes": ["cultural", "historical", "shopping", "nightlife"],
                "best_for": ["family", "couple", "solo", "friends"],
            },
            "edinburgh": {
                "name": "Edinburgh",
                "min_days": 2,
                "max_days": 4,
                "ideal_days": 2,
                "priority": 2,
                "highlights": ["Edinburgh Castle", "Royal Mile", "Arthur's Seat", "Old Town"],
                "vibes": ["historical", "cultural", "nature", "photography"],
                "best_for": ["couple", "solo", "friends"],
            },
            "bath": {
                "name": "Bath",
                "min_days": 1,
                "max_days": 2,
                "ideal_days": 1,
                "priority": 3,
                "highlights": ["Roman Baths", "Royal Crescent", "Thermae Bath Spa"],
                "vibes": ["relaxation", "historical", "romantic"],
                "best_for": ["couple", "solo", "seniors"],
            },
            "oxford": {
                "name": "Oxford",
                "min_days": 1,
                "max_days": 2,
                "ideal_days": 1,
                "priority": 3,
                "highlights": ["University Colleges", "Bodleian Library", "Ashmolean Museum"],
                "vibes": ["cultural", "historical", "academic"],
                "best_for": ["solo", "couple", "cultural"],
            },
        },
        "travel_times": {
            ("london", "edinburgh"): 270,
            ("london", "bath"): 90,
            ("london", "oxford"): 60,
            ("bath", "oxford"): 75,
        },
        "popular_routes": [
            ["london", "edinburgh"],
            ["london", "bath"],
            ["london", "oxford", "bath"],
        ],
    },
}


def get_travel_time(country_id: str, city1: str, city2: str) -> int:
    """Get travel time between two cities in minutes."""
    country = COUNTRY_DATABASE.get(country_id, {})
    travel_times = country.get("travel_times", {})

    key1 = (city1, city2)
    key2 = (city2, city1)

    if key1 in travel_times:
        return travel_times[key1]
    elif key2 in travel_times:
        return travel_times[key2]
    else:
        return 999  # Unknown route


def get_country_list() -> List[Dict]:
    """Get list of all countries with basic info."""
    countries = []
    for country_id, data in COUNTRY_DATABASE.items():
        cities = []
        for city_id, city_data in data["cities"].items():
            cities.append({
                "id": city_id,
                "name": city_data["name"],
                "country": data["name"],
                "min_days": city_data["min_days"],
                "max_days": city_data["max_days"],
                "ideal_days": city_data["ideal_days"],
                "highlights": city_data["highlights"],
                "vibes": city_data["vibes"],
                "best_for": city_data["best_for"],
                "travel_time_from": {},
            })

        countries.append({
            "id": country_id,
            "name": data["name"],
            "flag": data.get("flag", ""),
            "currency": data["currency"],
            "languages": data["languages"],
            "cities": cities,
            "popular_routes": data["popular_routes"],
        })

    return countries
