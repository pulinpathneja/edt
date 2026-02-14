"""
Seed Sample Data via API

Uses the deployed EDT API to seed sample data.
Run: python scripts/seed_via_api.py
"""

import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta
import random

API_BASE = "https://edt-api-724289610112.us-central1.run.app"

SAMPLE_POIS = [
    # Rome
    {"name": "Colosseum", "description": "Ancient Roman amphitheater, icon of Imperial Rome", "latitude": 41.8902, "longitude": 12.4922, "neighborhood": "Centro Storico", "city": "Rome", "country": "Italy", "category": "attraction", "subcategory": "historical", "typical_duration_minutes": 120, "best_time_of_day": "morning", "cost_level": 3, "avg_cost_per_person": 18.00},
    {"name": "Trevi Fountain", "description": "Baroque masterpiece, toss a coin for good luck", "latitude": 41.9009, "longitude": 12.4833, "neighborhood": "Trevi", "city": "Rome", "country": "Italy", "category": "attraction", "subcategory": "monument", "typical_duration_minutes": 45, "best_time_of_day": "evening", "cost_level": 1, "avg_cost_per_person": 0},
    {"name": "Vatican Museums", "description": "World-renowned art collection including the Sistine Chapel", "latitude": 41.9065, "longitude": 12.4536, "neighborhood": "Vatican City", "city": "Rome", "country": "Italy", "category": "attraction", "subcategory": "museum", "typical_duration_minutes": 180, "best_time_of_day": "morning", "cost_level": 4, "avg_cost_per_person": 25.00},
    {"name": "Pantheon", "description": "Best-preserved ancient Roman building with remarkable dome", "latitude": 41.8986, "longitude": 12.4768, "neighborhood": "Centro Storico", "city": "Rome", "country": "Italy", "category": "attraction", "subcategory": "historical", "typical_duration_minutes": 60, "best_time_of_day": "any", "cost_level": 1, "avg_cost_per_person": 5.00},
    {"name": "Trastevere", "description": "Charming bohemian neighborhood with trattorias", "latitude": 41.8867, "longitude": 12.4692, "neighborhood": "Trastevere", "city": "Rome", "country": "Italy", "category": "activity", "subcategory": "neighborhood", "typical_duration_minutes": 150, "best_time_of_day": "evening", "cost_level": 2, "avg_cost_per_person": 35.00},
    # Paris
    {"name": "Eiffel Tower", "description": "Iconic iron lattice tower and symbol of Paris", "latitude": 48.8584, "longitude": 2.2945, "neighborhood": "7th arrondissement", "city": "Paris", "country": "France", "category": "attraction", "subcategory": "landmark", "typical_duration_minutes": 120, "best_time_of_day": "evening", "cost_level": 3, "avg_cost_per_person": 28.00},
    {"name": "Louvre Museum", "description": "World's largest art museum, home to the Mona Lisa", "latitude": 48.8606, "longitude": 2.3376, "neighborhood": "1st arrondissement", "city": "Paris", "country": "France", "category": "attraction", "subcategory": "museum", "typical_duration_minutes": 240, "best_time_of_day": "morning", "cost_level": 3, "avg_cost_per_person": 17.00},
    {"name": "Montmartre", "description": "Artistic hilltop neighborhood with Sacré-Cœur", "latitude": 48.8867, "longitude": 2.3431, "neighborhood": "18th arrondissement", "city": "Paris", "country": "France", "category": "activity", "subcategory": "neighborhood", "typical_duration_minutes": 180, "best_time_of_day": "afternoon", "cost_level": 2, "avg_cost_per_person": 20.00},
    {"name": "Seine River Cruise", "description": "Romantic boat cruise past Paris landmarks", "latitude": 48.8588, "longitude": 2.3194, "neighborhood": "Seine", "city": "Paris", "country": "France", "category": "activity", "subcategory": "cruise", "typical_duration_minutes": 90, "best_time_of_day": "evening", "cost_level": 3, "avg_cost_per_person": 18.00},
    # Tokyo
    {"name": "Senso-ji Temple", "description": "Tokyo's oldest temple with iconic Thunder Gate", "latitude": 35.7148, "longitude": 139.7967, "neighborhood": "Asakusa", "city": "Tokyo", "country": "Japan", "category": "attraction", "subcategory": "temple", "typical_duration_minutes": 90, "best_time_of_day": "morning", "cost_level": 1, "avg_cost_per_person": 0},
    {"name": "Shibuya Crossing", "description": "World's busiest pedestrian crossing", "latitude": 35.6595, "longitude": 139.7004, "neighborhood": "Shibuya", "city": "Tokyo", "country": "Japan", "category": "attraction", "subcategory": "landmark", "typical_duration_minutes": 45, "best_time_of_day": "evening", "cost_level": 1, "avg_cost_per_person": 0},
    {"name": "TeamLab Borderless", "description": "Immersive digital art museum", "latitude": 35.6269, "longitude": 139.7839, "neighborhood": "Odaiba", "city": "Tokyo", "country": "Japan", "category": "attraction", "subcategory": "museum", "typical_duration_minutes": 180, "best_time_of_day": "any", "cost_level": 4, "avg_cost_per_person": 32.00},
    {"name": "Meiji Shrine", "description": "Peaceful Shinto shrine in forest setting", "latitude": 35.6764, "longitude": 139.6993, "neighborhood": "Harajuku", "city": "Tokyo", "country": "Japan", "category": "attraction", "subcategory": "shrine", "typical_duration_minutes": 75, "best_time_of_day": "morning", "cost_level": 1, "avg_cost_per_person": 0},
]

def api_request(method, endpoint, data=None, follow_redirects=True):
    """Make API request."""
    # Ensure trailing slash for POST requests
    if method == "POST" and not endpoint.endswith("/"):
        endpoint = endpoint + "/"

    url = f"{API_BASE}{endpoint}"
    headers = {"Content-Type": "application/json"}

    body = None
    if data:
        body = json.dumps(data).encode("utf-8")

    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        # Handle redirects manually
        if e.code in (301, 302, 307, 308) and follow_redirects:
            redirect_url = e.headers.get("Location")
            if redirect_url:
                print(f"  Following redirect to: {redirect_url}")
                req2 = urllib.request.Request(redirect_url, data=body, headers=headers, method=method)
                try:
                    with urllib.request.urlopen(req2, timeout=60) as response:
                        return json.loads(response.read().decode())
                except Exception as e2:
                    print(f"  Redirect error: {e2}")
                    return None
        error_body = e.read().decode()[:200] if e.fp else ""
        print(f"  HTTP Error {e.code}: {error_body}")
        return None
    except Exception as e:
        print(f"  Error: {e}")
        return None


def check_health():
    """Check API health."""
    print("Checking API health...")
    result = api_request("GET", "/health")
    if result:
        print(f"  API Status: {result.get('status', 'unknown')}")
        return True
    return False


def seed_pois():
    """Seed POIs via API."""
    print("\nSeeding POIs...")
    success = 0

    for poi in SAMPLE_POIS:
        result = api_request("POST", "/api/v1/pois", poi)
        if result:
            success += 1
            print(f"  Created: {poi['name']}")
        else:
            print(f"  Skipped (may exist): {poi['name']}")

    print(f"\nCreated {success}/{len(SAMPLE_POIS)} POIs")


def generate_itinerary(city):
    """Generate a sample itinerary."""
    print(f"\nGenerating itinerary for {city}...")

    start_date = datetime.now() + timedelta(days=random.randint(7, 30))
    end_date = start_date + timedelta(days=2)

    request_data = {
        "trip_request": {
            "destination_city": city,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "group_type": "couple",
            "group_size": 2,
            "vibes": ["cultural", "romantic"],
            "budget_level": 3,
            "pacing": "moderate",
            "has_kids": False,
            "has_seniors": False,
        },
        "must_include_pois": [],
        "exclude_pois": [],
    }

    result = api_request("POST", "/api/v1/itinerary/generate", request_data)
    if result:
        print(f"  Generated itinerary: {result.get('id', 'unknown')[:8]}...")
        if 'days' in result:
            print(f"  Days: {len(result['days'])}")
        return True
    return False


def main():
    print("=" * 60)
    print("EDT Sample Data Seeder (via API)")
    print("=" * 60)
    print(f"API: {API_BASE}")

    if not check_health():
        print("\nERROR: API is not healthy. Exiting.")
        return

    # Seed POIs
    seed_pois()

    # Generate sample itineraries
    for city in ["Rome", "Paris", "Tokyo"]:
        generate_itinerary(city)

    print("\n" + "=" * 60)
    print("DONE! Sample data seeded via API.")
    print("=" * 60)


if __name__ == "__main__":
    main()
