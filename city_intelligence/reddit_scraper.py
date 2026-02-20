"""
Reddit Scraper for City Intelligence
Collects posts and discussions about cities from travel subreddits.
Uses curated queries from TRAVEL_RESOURCES.md
"""
import asyncio
import httpx
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional
import json
import re
from urllib.parse import quote_plus


@dataclass
class RedditPost:
    id: str
    title: str
    selftext: str
    url: str
    subreddit: str
    score: int
    num_comments: int
    created_utc: float
    permalink: str
    category: str = ""
    relevance_score: float = 0.0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "selftext": self.selftext[:500] if self.selftext else "",
            "url": self.url,
            "subreddit": self.subreddit,
            "score": self.score,
            "num_comments": self.num_comments,
            "created_utc": self.created_utc,
            "permalink": f"https://reddit.com{self.permalink}",
            "category": self.category,
            "relevance_score": self.relevance_score,
        }


@dataclass
class CityRedditData:
    city_name: str
    country: str = ""
    collected_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    posts: list[RedditPost] = field(default_factory=list)
    subreddits_found: list[str] = field(default_factory=list)
    categories: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "city_name": self.city_name,
            "country": self.country,
            "collected_at": self.collected_at,
            "total_posts": len(self.posts),
            "subreddits_found": self.subreddits_found,
            "categories": {
                cat: [p.to_dict() for p in posts]
                for cat, posts in self.categories.items()
            },
            "top_posts": [p.to_dict() for p in sorted(self.posts, key=lambda x: x.relevance_score, reverse=True)[:20]],
        }


class RedditScraper:
    """
    Scrapes Reddit for city-related travel information.
    Uses Reddit's JSON API (no OAuth required for read-only).
    """

    BASE_URL = "https://www.reddit.com"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) CityIntelBot/1.0"
    }

    def __init__(self, rate_limit_delay: float = 2.0):
        self.rate_limit_delay = rate_limit_delay
        self.client = httpx.AsyncClient(
            headers=self.HEADERS,
            timeout=30.0,
            follow_redirects=True,
        )

    async def close(self):
        await self.client.aclose()

    async def _fetch_json(self, url: str) -> Optional[dict]:
        """Fetch JSON from Reddit API with rate limiting."""
        try:
            await asyncio.sleep(self.rate_limit_delay)
            response = await self.client.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"  [Reddit] {response.status_code} for {url[:120]}")
                return None
        except Exception as e:
            print(f"  [Reddit] Error: {e}")
            return None

    async def check_subreddit_exists(self, subreddit: str) -> bool:
        """Check if a subreddit exists and is active."""
        url = f"{self.BASE_URL}/r/{subreddit}/about.json"
        data = await self._fetch_json(url)
        if data and "data" in data:
            sub_data = data.get("data", {})
            subscribers = sub_data.get("subscribers", 0) or 0
            if subscribers > 100:
                return True
        return False

    async def search_subreddit(
        self,
        subreddit: str,
        query: str,
        limit: int = 25,
        sort: str = "relevance",
        time_filter: str = "year"
    ) -> list[RedditPost]:
        """Search within a subreddit."""
        encoded_query = quote_plus(query)
        url = (f"{self.BASE_URL}/r/{subreddit}/search.json"
               f"?q={encoded_query}&restrict_sr=1&sort={sort}&t={time_filter}&limit={limit}")

        data = await self._fetch_json(url)
        if not data or "data" not in data:
            return []

        return self._parse_posts(data)

    async def get_top_posts(
        self,
        subreddit: str,
        time_filter: str = "year",
        limit: int = 25
    ) -> list[RedditPost]:
        """Get top posts from a subreddit."""
        url = f"{self.BASE_URL}/r/{subreddit}/top.json?t={time_filter}&limit={limit}"

        data = await self._fetch_json(url)
        if not data or "data" not in data:
            return []

        return self._parse_posts(data)

    async def search_global(
        self,
        query: str,
        limit: int = 25,
        sort: str = "relevance"
    ) -> list[RedditPost]:
        """Search across all of Reddit."""
        encoded_query = quote_plus(query)
        url = f"{self.BASE_URL}/search.json?q={encoded_query}&sort={sort}&limit={limit}"

        data = await self._fetch_json(url)
        if not data or "data" not in data:
            return []

        return self._parse_posts(data)

    def _parse_posts(self, data: dict) -> list[RedditPost]:
        """Parse Reddit JSON response into RedditPost objects."""
        posts = []
        for child in data["data"].get("children", []):
            post_data = child.get("data", {})
            posts.append(RedditPost(
                id=post_data.get("id", ""),
                title=post_data.get("title", ""),
                selftext=post_data.get("selftext", ""),
                url=post_data.get("url", ""),
                subreddit=post_data.get("subreddit", ""),
                score=post_data.get("score", 0),
                num_comments=post_data.get("num_comments", 0),
                created_utc=post_data.get("created_utc", 0),
                permalink=post_data.get("permalink", ""),
            ))
        return posts

    def is_relevant(self, post: RedditPost, city: str, country: str = "") -> bool:
        """
        Check if a post is actually about the target city.
        Filters out posts about wrong cities with same name (Florence SC vs Florence Italy).
        """
        text = f"{post.title} {post.selftext}".lower()
        city_lower = city.lower()

        # Must mention the city in title or body
        if city_lower not in text:
            return False

        # If country is specified, check for wrong-city disambiguation
        if country:
            country_lower = country.lower()
            # If country is mentioned, definitely relevant
            if country_lower in text:
                return True

            # Reject known wrong-country signals
            wrong_signals = {
                "florence": ["south carolina", "florence sc", "florence, sc", "alabama", "oregon", "kentucky"],
                "paris": ["paris texas", "paris, tx", "paris tx"],
                "rome": ["rome ga", "rome, ga", "rome georgia"],
                "naples": ["naples fl", "naples, fl", "naples florida", "naples marco"],
                "bath": ["bathroom", "bathtub", "bath bomb", "bath salt"],
                "nice": ["nice guy", "nice try", "nice job", "nice work"],
            }
            wrong = wrong_signals.get(city_lower, [])
            for signal in wrong:
                if signal in text:
                    return False

        return True

    def calculate_relevance(self, post: RedditPost, city: str, country: str, category: str) -> float:
        """
        Calculate relevance score for a post.
        Based on quality indicators from TRAVEL_RESOURCES.md:
        - Upvotes > 100, Comments > 20, Recent < 2 years
        Penalises AMA/meta posts and posts missing city from title.
        """
        score = 0.0
        title_lower = post.title.lower()
        text = f"{post.title} {post.selftext}".lower()
        city_lower = city.lower()
        country_lower = country.lower() if country else ""

        # City in title (strongest signal)
        if city_lower in title_lower:
            score += 3.0
        else:
            # Penalty: city not in title means weaker relevance
            score -= 1.0

        # City in body
        if city_lower in (post.selftext or "").lower():
            score += 1.0

        # Country mentioned (confirms disambiguation)
        if country_lower and country_lower in text:
            score += 2.0

        # Penalty: AMA / meta posts are almost never useful travel tips
        ama_signals = ["ama", "ask me anything", "i am a", "i'm a", "iama"]
        if any(sig in title_lower for sig in ama_signals):
            score -= 3.0

        # Upvote quality (per TRAVEL_RESOURCES.md thresholds)
        if post.score > 100:
            score += 2.0
        elif post.score > 50:
            score += 1.5
        elif post.score > 20:
            score += 1.0
        elif post.score > 5:
            score += 0.5

        # Comment engagement (per TRAVEL_RESOURCES.md: Comments > 20)
        if post.num_comments > 50:
            score += 1.5
        elif post.num_comments > 20:
            score += 1.0
        elif post.num_comments > 5:
            score += 0.5

        # Recency (per TRAVEL_RESOURCES.md: < 2 years)
        post_age_days = (datetime.utcnow().timestamp() - post.created_utc) / 86400
        if post_age_days < 90:
            score += 2.0
        elif post_age_days < 180:
            score += 1.5
        elif post_age_days < 365:
            score += 1.0
        elif post_age_days < 730:  # < 2 years
            score += 0.5
        # > 2 years: no bonus

        # Travel-focused subreddit bonus
        travel_subs = [
            "travel", "solotravel", "shoestring", "backpacking", "travelhacks",
            "europetravel", "japantravel", "italytravel",
        ]
        if post.subreddit.lower() in travel_subs:
            score += 1.0

        return score


# --- Curated subreddit mappings from TRAVEL_RESOURCES.md ---

# General travel communities (7M+, 1.8M+, 1M+, 500K+, 400K+)
GENERAL_TRAVEL_SUBREDDITS = ["travel", "solotravel", "shoestring", "TravelHacks", "backpacking"]

# Country-specific travel subreddits
COUNTRY_TRAVEL_SUBREDDITS = {
    "italy": ["ItalyTravel", "italy", "ItalyTourism"],
    "france": ["france", "ParisTravelGuide"],
    "spain": ["spain", "VisitSpain"],
    "japan": ["JapanTravel", "JapanTourism", "japan"],
    "uk": ["uktravel", "unitedkingdom"],
    "germany": ["germany", "GermanyTravel"],
    "greece": ["greece", "GreeceTravel"],
    "portugal": ["portugal"],
    "thailand": ["ThailandTourism", "Thailand"],
    "india": ["india", "IncredibleIndia"],
    "netherlands": ["Netherlands"],
    "czech republic": ["czech"],
    "austria": ["austria"],
}

# Known active city subreddits
KNOWN_CITY_SUBREDDITS = {
    "rome": ["rome"],
    "florence": ["florence"],
    "venice": ["venice"],
    "milan": ["milano"],
    "naples": ["napoli"],
    "paris": ["paris", "ParisTravelGuide"],
    "nice": ["nice"],
    "lyon": ["lyon"],
    "bordeaux": ["bordeaux"],
    "barcelona": ["barcelona"],
    "madrid": ["madrid"],
    "seville": ["seville"],
    "tokyo": ["tokyo"],
    "kyoto": ["kyoto"],
    "osaka": ["osaka"],
    "london": ["london"],
    "edinburgh": ["Edinburgh"],
    "bath": ["bath"],
    "oxford": ["oxford"],
}


# --- Search queries from TRAVEL_RESOURCES.md Section 5 ---

SEARCH_QUERIES = {
    "hidden_gems": [
        '"{city}" hidden gems locals',
        '"{city}" off the beaten path',
        '"{city}" secret spots',
        '"{city}" underrated places',
    ],
    "things_to_do": [
        '"{city}" things to do',
        '"{city}" must see attractions',
        '"{city}" itinerary',
        '"{city}" worth visiting why',
    ],
    "food": [
        '"{city}" best local food',
        '"{city}" where locals eat',
        '"{city}" street food',
        '"{city}" food markets',
    ],
    "safety_challenges": [
        '"{city}" safety concerns',
        '"{city}" areas to avoid',
        '"{city}" tourist scams',
        '"{city}" avoid tourist traps',
    ],
    "family": [
        '"{city}" with kids things to do',
        '"{city}" family friendly activities',
        '"{city}" stroller friendly',
    ],
    "neighborhoods": [
        '"{city}" best walking neighborhoods',
        '"{city}" where to stay area',
        '"{city}" walkable areas',
    ],
    "budget": [
        '"{city}" budget tips cheap',
        '"{city}" free things to do',
    ],
    "pros_cons": [
        '"{city}" pros and cons',
        '"{city}" honest review tourist',
        '"{city}" overrated underrated',
    ],
}


class CityIntelligenceCollector:
    """
    Collects comprehensive city intelligence from Reddit.
    Uses curated queries from TRAVEL_RESOURCES.md.
    All searches include city + country context to avoid irrelevant results.
    Posts are filtered to ensure they actually mention the target city.
    """

    def __init__(self, scraper: RedditScraper):
        self.scraper = scraper

    async def collect_city_data(self, city: str, country: str = "") -> CityRedditData:
        """Collect Reddit data for a city with proper country context."""
        print(f"\n{'='*50}")
        print(f"Collecting Reddit data for: {city}, {country}")
        print(f"{'='*50}")

        data = CityRedditData(city_name=city, country=country)
        all_posts = []
        seen_ids = set()

        def _add_post(post: RedditPost, category: str):
            """Add a post if relevant and not duplicate."""
            if post.id in seen_ids:
                return
            if not self.scraper.is_relevant(post, city, country):
                return
            post.category = category
            post.relevance_score = self.scraper.calculate_relevance(post, city, country, category)
            all_posts.append(post)
            seen_ids.add(post.id)

        # --- Step 1: Search city-specific subreddits ---
        city_key = city.lower().replace(" ", "")
        city_subs = list(KNOWN_CITY_SUBREDDITS.get(city_key, []))

        # Auto-discover r/{city} and r/visit{city}
        for pattern in [city_key, f"visit{city_key}"]:
            if pattern not in [s.lower() for s in city_subs]:
                if await self.scraper.check_subreddit_exists(pattern):
                    city_subs.append(pattern)
                    print(f"  Discovered: r/{pattern}")

        data.subreddits_found = list(city_subs)
        print(f"\n  City subreddits: {city_subs}")

        for sub in city_subs:
            print(f"  Searching r/{sub}...")

            # Use curated queries from TRAVEL_RESOURCES.md (with city name quoted)
            for category, query_templates in SEARCH_QUERIES.items():
                for template in query_templates[:2]:  # Top 2 queries per category
                    query = template.replace("{city}", city)
                    posts = await self.scraper.search_subreddit(sub, query, limit=15, time_filter="all")
                    for post in posts:
                        _add_post(post, category)

            # Top posts from city subreddit (high quality by definition)
            top_posts = await self.scraper.get_top_posts(sub, time_filter="all", limit=25)
            for post in top_posts:
                _add_post(post, "top_posts")

        # --- Step 2: Search country-specific travel subreddits ---
        country_key = country.lower() if country else ""
        country_subs = COUNTRY_TRAVEL_SUBREDDITS.get(country_key, [])
        print(f"\n  Country travel subs: {country_subs}")

        for sub in country_subs:
            print(f"  Searching r/{sub} for '{city}'...")
            # In country subs, always include the city name in the query
            for category, query_templates in SEARCH_QUERIES.items():
                query = query_templates[0].replace("{city}", city)  # Top query per category
                posts = await self.scraper.search_subreddit(sub, query, limit=10)
                for post in posts:
                    _add_post(post, category)

        # --- Step 3: Search general travel subreddits with full context ---
        search_prefix = f"{city} {country}" if country else city
        print(f"\n  Searching general travel subs for '{search_prefix}'...")

        for sub in GENERAL_TRAVEL_SUBREDDITS:
            # Focused queries: city + country + topic
            for category, query_templates in SEARCH_QUERIES.items():
                query = query_templates[0].replace("{city}", search_prefix)
                posts = await self.scraper.search_subreddit(sub, query, limit=10)
                for post in posts:
                    _add_post(post, category)

        # --- Step 4: Global Reddit search with strong context ---
        print(f"\n  Global search for '{search_prefix}'...")
        for suffix in ["travel guide tips", "itinerary recommendations", "must visit hidden gems"]:
            global_posts = await self.scraper.search_global(f'"{city}" {country} {suffix}', limit=15)
            for post in global_posts:
                _add_post(post, "general")

        # --- Filter & organize ---
        # Keep only posts with minimum quality (relevance >= 3.0)
        # Requires city in title, OR city-in-body + country mention
        all_posts = [p for p in all_posts if p.relevance_score >= 3.0]
        all_posts.sort(key=lambda x: x.relevance_score, reverse=True)

        data.posts = all_posts
        for post in all_posts:
            if post.category not in data.categories:
                data.categories[post.category] = []
            data.categories[post.category].append(post)

        # Sort each category by relevance
        for category in data.categories:
            data.categories[category].sort(key=lambda x: x.relevance_score, reverse=True)

        print(f"\n  Result: {len(all_posts)} relevant posts across {len(data.categories)} categories")
        if seen_ids:
            filtered = len(seen_ids) - len(all_posts)
            if filtered > 0:
                print(f"  (filtered out {filtered} low-relevance or off-topic posts)")
        return data


async def collect_city_intelligence(city: str, country: str = "", output_file: Optional[str] = None) -> CityRedditData:
    """
    Main function to collect city intelligence from Reddit.

    Args:
        city: Name of the city to research (e.g., "Florence")
        country: Country name for disambiguation (e.g., "Italy")
        output_file: Optional path to save JSON output

    Returns:
        CityRedditData object with collected information
    """
    # Auto-detect country if not provided
    if not country:
        country = _guess_country(city)

    scraper = RedditScraper(rate_limit_delay=2.0)
    collector = CityIntelligenceCollector(scraper)

    try:
        data = await collector.collect_city_data(city, country)

        if output_file:
            with open(output_file, 'w') as f:
                json.dump(data.to_dict(), f, indent=2)
            print(f"\nSaved to {output_file}")

        return data
    finally:
        await scraper.close()


def _guess_country(city: str) -> str:
    """Auto-detect country from known city names."""
    city_country_map = {
        "rome": "Italy", "florence": "Italy", "venice": "Italy",
        "milan": "Italy", "naples": "Italy", "amalfi": "Italy",
        "paris": "France", "nice": "France", "lyon": "France", "bordeaux": "France",
        "barcelona": "Spain", "madrid": "Spain", "seville": "Spain", "granada": "Spain",
        "tokyo": "Japan", "kyoto": "Japan", "osaka": "Japan", "hiroshima": "Japan",
        "london": "UK", "edinburgh": "UK", "bath": "UK", "oxford": "UK",
        "berlin": "Germany", "munich": "Germany",
        "amsterdam": "Netherlands", "prague": "Czech Republic",
        "vienna": "Austria", "lisbon": "Portugal", "athens": "Greece",
        "bangkok": "Thailand", "delhi": "India", "mumbai": "India",
    }
    return city_country_map.get(city.lower(), "")


# CLI usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python reddit_scraper.py <city_name> [country] [output_file]")
        sys.exit(1)

    city = sys.argv[1]
    country = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].endswith(".json") else ""
    output_file = sys.argv[-1] if sys.argv[-1].endswith(".json") else f"city_intelligence/cities/{city.lower().replace(' ', '_')}_reddit.json"

    asyncio.run(collect_city_intelligence(city, country, output_file))
