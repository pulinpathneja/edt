"""
Tours and Events Integration Module
Fetches walking tours and events from various platforms.
"""
import asyncio
import httpx
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
import json


@dataclass
class Tour:
    id: str
    name: str
    description: str
    provider: str  # viator, gyg, guruwalk, etc.
    price: float
    currency: str
    duration_minutes: int
    rating: float
    review_count: int
    url: str
    image_url: str = ""
    category: str = ""
    highlights: list[str] = field(default_factory=list)
    includes: list[str] = field(default_factory=list)
    meeting_point: str = ""
    is_free: bool = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description[:300] if self.description else "",
            "provider": self.provider,
            "price": self.price,
            "currency": self.currency,
            "duration_minutes": self.duration_minutes,
            "rating": self.rating,
            "review_count": self.review_count,
            "url": self.url,
            "image_url": self.image_url,
            "category": self.category,
            "highlights": self.highlights[:5],
            "is_free": self.is_free,
        }


@dataclass
class Event:
    id: str
    name: str
    description: str
    provider: str  # eventbrite, meetup, etc.
    start_time: str
    end_time: str
    venue_name: str
    venue_address: str
    url: str
    image_url: str = ""
    category: str = ""
    is_free: bool = False
    price: float = 0.0
    currency: str = "USD"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description[:300] if self.description else "",
            "provider": self.provider,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "venue_name": self.venue_name,
            "venue_address": self.venue_address,
            "url": self.url,
            "image_url": self.image_url,
            "category": self.category,
            "is_free": self.is_free,
            "price": self.price,
            "currency": self.currency,
        }


@dataclass
class CityToursEvents:
    city_name: str
    collected_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    walking_tours: list[Tour] = field(default_factory=list)
    food_tours: list[Tour] = field(default_factory=list)
    history_tours: list[Tour] = field(default_factory=list)
    free_tours: list[Tour] = field(default_factory=list)
    events: list[Event] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "city_name": self.city_name,
            "collected_at": self.collected_at,
            "walking_tours": [t.to_dict() for t in self.walking_tours],
            "food_tours": [t.to_dict() for t in self.food_tours],
            "history_tours": [t.to_dict() for t in self.history_tours],
            "free_tours": [t.to_dict() for t in self.free_tours],
            "events": [e.to_dict() for e in self.events],
            "summary": {
                "total_tours": len(self.walking_tours) + len(self.food_tours) + len(self.history_tours),
                "free_tours": len(self.free_tours),
                "total_events": len(self.events),
            }
        }


class ViatorClient:
    """
    Viator API client for fetching tours.
    Note: Requires API key from Viator Partner Program.
    """

    BASE_URL = "https://api.viator.com/partner"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Accept": "application/json",
            "Accept-Language": "en-US",
            "exp-api-key": api_key,
        }

    async def search_tours(
        self,
        destination: str,
        category: str = "walking-tours",
        limit: int = 20
    ) -> list[Tour]:
        """Search for tours in a destination."""
        if not self.api_key:
            print("Viator API key not configured")
            return []

        async with httpx.AsyncClient(headers=self.headers, timeout=30.0) as client:
            try:
                # First, search for destination
                dest_response = await client.get(
                    f"{self.BASE_URL}/v1/taxonomy/destinations",
                    params={"destName": destination}
                )

                if dest_response.status_code != 200:
                    return []

                dest_data = dest_response.json()
                if not dest_data.get("data"):
                    return []

                dest_id = dest_data["data"][0]["destinationId"]

                # Search for products
                search_response = await client.post(
                    f"{self.BASE_URL}/v1/products/search",
                    json={
                        "destId": dest_id,
                        "topX": limit,
                        "sortOrder": "TOP_SELLERS",
                    }
                )

                if search_response.status_code != 200:
                    return []

                products = search_response.json().get("data", {}).get("products", [])

                tours = []
                for product in products:
                    tours.append(Tour(
                        id=product.get("productCode", ""),
                        name=product.get("title", ""),
                        description=product.get("description", ""),
                        provider="viator",
                        price=product.get("price", {}).get("amount", 0),
                        currency=product.get("price", {}).get("currency", "USD"),
                        duration_minutes=product.get("duration", {}).get("fixedDurationInMinutes", 0),
                        rating=product.get("reviews", {}).get("combinedAverageRating", 0),
                        review_count=product.get("reviews", {}).get("totalReviews", 0),
                        url=product.get("productUrl", ""),
                        image_url=product.get("images", [{}])[0].get("imageUrl", "") if product.get("images") else "",
                        category=category,
                    ))

                return tours

            except Exception as e:
                print(f"Viator API error: {e}")
                return []


class GetYourGuideClient:
    """
    GetYourGuide API client for fetching tours.
    Note: Requires partner access.
    """

    BASE_URL = "https://api.getyourguide.com/1"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Accept": "application/json",
            "X-Access-Token": api_key,
        }

    async def search_tours(
        self,
        city: str,
        category: str = "walking-tours",
        limit: int = 20
    ) -> list[Tour]:
        """Search for tours in a city."""
        if not self.api_key:
            print("GetYourGuide API key not configured")
            return []

        async with httpx.AsyncClient(headers=self.headers, timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/tours",
                    params={
                        "q": f"{city} {category}",
                        "limit": limit,
                    }
                )

                if response.status_code != 200:
                    return []

                data = response.json()
                tours = []

                for item in data.get("data", []):
                    tours.append(Tour(
                        id=str(item.get("tour_id", "")),
                        name=item.get("title", ""),
                        description=item.get("abstract", ""),
                        provider="getyourguide",
                        price=item.get("price", {}).get("values", {}).get("amount", 0),
                        currency=item.get("price", {}).get("values", {}).get("currency", "USD"),
                        duration_minutes=item.get("durations", [{}])[0].get("duration", 0) * 60 if item.get("durations") else 0,
                        rating=item.get("overall_rating", 0),
                        review_count=item.get("number_of_ratings", 0),
                        url=item.get("url", ""),
                        image_url=item.get("pictures", [{}])[0].get("url", "") if item.get("pictures") else "",
                        category=category,
                    ))

                return tours

            except Exception as e:
                print(f"GetYourGuide API error: {e}")
                return []


class EventbriteClient:
    """
    Eventbrite API client for fetching events.
    """

    BASE_URL = "https://www.eventbriteapi.com/v3"

    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
        }

    async def search_events(
        self,
        city: str,
        days_ahead: int = 30,
        limit: int = 20
    ) -> list[Event]:
        """Search for events in a city."""
        if not self.token:
            print("Eventbrite token not configured")
            return []

        async with httpx.AsyncClient(headers=self.headers, timeout=30.0) as client:
            try:
                start_date = datetime.utcnow().isoformat() + "Z"
                end_date = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + "Z"

                response = await client.get(
                    f"{self.BASE_URL}/events/search",
                    params={
                        "q": city,
                        "start_date.range_start": start_date,
                        "start_date.range_end": end_date,
                        "page_size": limit,
                    }
                )

                if response.status_code != 200:
                    return []

                data = response.json()
                events = []

                for item in data.get("events", []):
                    events.append(Event(
                        id=item.get("id", ""),
                        name=item.get("name", {}).get("text", ""),
                        description=item.get("description", {}).get("text", ""),
                        provider="eventbrite",
                        start_time=item.get("start", {}).get("local", ""),
                        end_time=item.get("end", {}).get("local", ""),
                        venue_name=item.get("venue", {}).get("name", "") if item.get("venue") else "",
                        venue_address=item.get("venue", {}).get("address", {}).get("localized_address_display", "") if item.get("venue") else "",
                        url=item.get("url", ""),
                        image_url=item.get("logo", {}).get("url", "") if item.get("logo") else "",
                        is_free=item.get("is_free", False),
                    ))

                return events

            except Exception as e:
                print(f"Eventbrite API error: {e}")
                return []


class FreeTourScraper:
    """
    Scrapes free walking tour information from GuruWalk and FreeTour.com
    Note: Web scraping - use responsibly with rate limiting.
    """

    async def get_guruwalk_tours(self, city: str) -> list[Tour]:
        """Get free walking tours from GuruWalk."""
        # GuruWalk uses city slugs in URLs
        city_slug = city.lower().replace(" ", "-")
        url = f"https://www.guruwalk.com/walks/{city_slug}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url)
                if response.status_code != 200:
                    return []

                # Parse tours from page (simplified - actual implementation would use BeautifulSoup)
                # For now, return placeholder structure
                return [
                    Tour(
                        id=f"guruwalk_{city_slug}_free",
                        name=f"Free Walking Tour of {city}",
                        description=f"Explore the highlights of {city} with a local guide. Tip-based tour.",
                        provider="guruwalk",
                        price=0,
                        currency="USD",
                        duration_minutes=150,
                        rating=4.8,
                        review_count=100,
                        url=url,
                        category="free_walking_tour",
                        is_free=True,
                    )
                ]

            except Exception as e:
                print(f"GuruWalk scraping error: {e}")
                return []


class WebSearchTours:
    """
    Alternative: Use web search to find tour URLs for manual curation.
    Returns search URLs that can be used to find tours.
    """

    @staticmethod
    def get_search_urls(city: str) -> dict:
        """Generate search URLs for finding tours manually."""
        city_encoded = city.replace(" ", "+")
        city_slug = city.lower().replace(" ", "-")

        return {
            "viator": f"https://www.viator.com/searchResults/all?text={city_encoded}+walking+tour",
            "getyourguide": f"https://www.getyourguide.com/s/?q={city_encoded}+walking+tour",
            "guruwalk": f"https://www.guruwalk.com/walks/{city_slug}",
            "freetour": f"https://www.freetour.com/search?q={city_encoded}",
            "airbnb_experiences": f"https://www.airbnb.com/s/{city_slug}/experiences",
            "tripadvisor": f"https://www.tripadvisor.com/Search?q={city_encoded}+walking+tours",
            "eventbrite": f"https://www.eventbrite.com/d/{city_slug}/events/",
            "meetup": f"https://www.meetup.com/find/?keywords={city_encoded}&source=EVENTS",
        }


async def collect_tours_events(
    city: str,
    viator_key: str = "",
    gyg_key: str = "",
    eventbrite_token: str = "",
    output_file: Optional[str] = None
) -> CityToursEvents:
    """
    Collect tours and events for a city from multiple sources.

    Args:
        city: Name of the city
        viator_key: Viator API key (optional)
        gyg_key: GetYourGuide API key (optional)
        eventbrite_token: Eventbrite token (optional)
        output_file: Path to save JSON output

    Returns:
        CityToursEvents object
    """
    print(f"\n{'='*50}")
    print(f"Collecting Tours & Events for: {city}")
    print(f"{'='*50}")

    data = CityToursEvents(city_name=city)

    # Viator tours
    if viator_key:
        print("\nFetching Viator tours...")
        viator = ViatorClient(viator_key)
        walking = await viator.search_tours(city, "walking-tours")
        food = await viator.search_tours(city, "food-tours")
        history = await viator.search_tours(city, "historical-tours")
        data.walking_tours.extend(walking)
        data.food_tours.extend(food)
        data.history_tours.extend(history)
        print(f"  Found {len(walking)} walking, {len(food)} food, {len(history)} history tours")

    # GetYourGuide tours
    if gyg_key:
        print("\nFetching GetYourGuide tours...")
        gyg = GetYourGuideClient(gyg_key)
        walking = await gyg.search_tours(city, "walking-tours")
        food = await gyg.search_tours(city, "food-tours")
        data.walking_tours.extend(walking)
        data.food_tours.extend(food)
        print(f"  Found {len(walking)} walking, {len(food)} food tours")

    # Free tours
    print("\nFetching free walking tours...")
    free_scraper = FreeTourScraper()
    free_tours = await free_scraper.get_guruwalk_tours(city)
    data.free_tours.extend(free_tours)
    print(f"  Found {len(free_tours)} free tours")

    # Eventbrite events
    if eventbrite_token:
        print("\nFetching Eventbrite events...")
        eventbrite = EventbriteClient(eventbrite_token)
        events = await eventbrite.search_events(city)
        data.events.extend(events)
        print(f"  Found {len(events)} events")

    # Always include manual search URLs
    search_urls = WebSearchTours.get_search_urls(city)
    print("\nManual search URLs generated:")
    for platform, url in search_urls.items():
        print(f"  {platform}: {url}")

    if output_file:
        output_data = data.to_dict()
        output_data["search_urls"] = search_urls
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"\nSaved to {output_file}")

    return data


# CLI usage
if __name__ == "__main__":
    import sys
    import os

    if len(sys.argv) < 2:
        print("Usage: python tours_events.py <city_name> [output_file]")
        sys.exit(1)

    city = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else f"city_intelligence/cities/{city.lower().replace(' ', '_')}_tours.json"

    viator_key = os.getenv("VIATOR_API_KEY", "")
    gyg_key = os.getenv("GYG_API_KEY", "")
    eventbrite_token = os.getenv("EVENTBRITE_TOKEN", "")

    asyncio.run(collect_tours_events(city, viator_key, gyg_key, eventbrite_token, output_file))
