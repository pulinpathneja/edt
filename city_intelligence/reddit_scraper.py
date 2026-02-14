"""
Reddit Scraper for City Intelligence
Collects posts and discussions about cities from travel subreddits.
"""
import asyncio
import httpx
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional
import json
import re


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
    collected_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    posts: list[RedditPost] = field(default_factory=list)
    subreddits_found: list[str] = field(default_factory=list)
    categories: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "city_name": self.city_name,
            "collected_at": self.collected_at,
            "total_posts": len(self.posts),
            "subreddits_found": self.subreddits_found,
            "categories": {
                cat: [p.to_dict() for p in posts]
                for cat, posts in self.categories.items()
            },
            "top_posts": [p.to_dict() for p in sorted(self.posts, key=lambda x: x.score, reverse=True)[:20]],
        }


class RedditScraper:
    """
    Scrapes Reddit for city-related travel information.
    Uses Reddit's JSON API (no OAuth required for read-only).
    """

    BASE_URL = "https://www.reddit.com"
    HEADERS = {
        "User-Agent": "CityIntelBot/1.0 (City Intelligence Collector)"
    }

    def __init__(self, rate_limit_delay: float = 2.0):
        self.rate_limit_delay = rate_limit_delay
        self.client = httpx.AsyncClient(headers=self.HEADERS, timeout=30.0)

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
                print(f"Error fetching {url}: {response.status_code}")
                return None
        except Exception as e:
            print(f"Exception fetching {url}: {e}")
            return None

    async def check_subreddit_exists(self, subreddit: str) -> bool:
        """Check if a subreddit exists."""
        url = f"{self.BASE_URL}/r/{subreddit}/about.json"
        data = await self._fetch_json(url)
        return data is not None and "data" in data

    async def search_subreddit(
        self,
        subreddit: str,
        query: str,
        limit: int = 25,
        sort: str = "relevance",
        time_filter: str = "year"
    ) -> list[RedditPost]:
        """Search within a subreddit."""
        url = f"{self.BASE_URL}/r/{subreddit}/search.json"
        params = {
            "q": query,
            "restrict_sr": "1",
            "sort": sort,
            "t": time_filter,
            "limit": limit,
        }
        url_with_params = f"{url}?{'&'.join(f'{k}={v}' for k, v in params.items())}"

        data = await self._fetch_json(url_with_params)
        if not data or "data" not in data:
            return []

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

    async def search_global(
        self,
        query: str,
        limit: int = 25,
        sort: str = "relevance"
    ) -> list[RedditPost]:
        """Search across all of Reddit."""
        url = f"{self.BASE_URL}/search.json"
        params = {
            "q": query,
            "sort": sort,
            "limit": limit,
        }
        url_with_params = f"{url}?{'&'.join(f'{k}={v}' for k, v in params.items())}"

        data = await self._fetch_json(url_with_params)
        if not data or "data" not in data:
            return []

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

    def calculate_relevance(self, post: RedditPost, city: str, category: str) -> float:
        """Calculate relevance score for a post."""
        score = 0.0

        # Title contains city name
        if city.lower() in post.title.lower():
            score += 2.0

        # High upvotes
        if post.score > 100:
            score += 1.5
        elif post.score > 50:
            score += 1.0
        elif post.score > 20:
            score += 0.5

        # High engagement
        if post.num_comments > 50:
            score += 1.0
        elif post.num_comments > 20:
            score += 0.5

        # Recent post
        post_age_days = (datetime.utcnow().timestamp() - post.created_utc) / 86400
        if post_age_days < 180:
            score += 1.0
        elif post_age_days < 365:
            score += 0.5

        # From travel subreddit
        travel_subs = ["travel", "solotravel", "shoestring", "backpacking"]
        if post.subreddit.lower() in travel_subs:
            score += 0.5

        return score


class CityIntelligenceCollector:
    """
    Collects comprehensive city intelligence from Reddit.
    """

    SEARCH_CATEGORIES = {
        "general": ["things to do", "must see", "hidden gems", "local tips"],
        "challenges": ["problems", "avoid", "scams", "safety"],
        "pros_cons": ["pros cons", "worth visiting", "overrated underrated"],
        "family": ["with kids", "family friendly", "stroller", "playground"],
        "food": ["best food", "where locals eat", "street food", "cheap eats"],
        "neighborhoods": ["best neighborhood", "walkable", "where to stay"],
        "budget": ["budget", "cheap", "free things"],
        "nightlife": ["nightlife", "bars", "clubs"],
    }

    CITY_SUBREDDIT_PATTERNS = [
        "{city}",
        "Ask{city}",
        "{city}food",
        "visit{city}",
    ]

    TRAVEL_SUBREDDITS = ["travel", "solotravel", "shoestring", "backpacking"]

    def __init__(self, scraper: RedditScraper):
        self.scraper = scraper

    async def find_city_subreddits(self, city: str) -> list[str]:
        """Find city-specific subreddits."""
        found = []
        city_normalized = city.lower().replace(" ", "")

        for pattern in self.CITY_SUBREDDIT_PATTERNS:
            subreddit = pattern.format(city=city_normalized)
            if await self.scraper.check_subreddit_exists(subreddit):
                found.append(subreddit)
                print(f"  Found subreddit: r/{subreddit}")

        # Also check capitalized versions
        city_cap = city.replace(" ", "")
        for pattern in self.CITY_SUBREDDIT_PATTERNS:
            subreddit = pattern.format(city=city_cap)
            if subreddit.lower() not in [s.lower() for s in found]:
                if await self.scraper.check_subreddit_exists(subreddit):
                    found.append(subreddit)
                    print(f"  Found subreddit: r/{subreddit}")

        return found

    async def collect_city_data(self, city: str) -> CityRedditData:
        """Collect comprehensive Reddit data for a city."""
        print(f"\n{'='*50}")
        print(f"Collecting Reddit data for: {city}")
        print(f"{'='*50}")

        data = CityRedditData(city_name=city)

        # Find city-specific subreddits
        print("\nSearching for city subreddits...")
        city_subs = await self.find_city_subreddits(city)
        data.subreddits_found = city_subs

        all_posts = []
        seen_ids = set()

        # Search city subreddits
        for sub in city_subs:
            print(f"\nSearching r/{sub}...")
            for category, queries in self.SEARCH_CATEGORIES.items():
                for query in queries:
                    posts = await self.scraper.search_subreddit(sub, query, limit=10)
                    for post in posts:
                        if post.id not in seen_ids:
                            post.category = category
                            post.relevance_score = self.scraper.calculate_relevance(post, city, category)
                            all_posts.append(post)
                            seen_ids.add(post.id)

            # Also get top posts
            top_posts = await self.scraper.get_top_posts(sub, limit=25)
            for post in top_posts:
                if post.id not in seen_ids:
                    post.category = "top_posts"
                    post.relevance_score = self.scraper.calculate_relevance(post, city, "top_posts")
                    all_posts.append(post)
                    seen_ids.add(post.id)

        # Search travel subreddits for city mentions
        print("\nSearching travel subreddits...")
        for sub in self.TRAVEL_SUBREDDITS:
            for category, queries in self.SEARCH_CATEGORIES.items():
                for query in queries[:2]:  # Limit queries per category
                    full_query = f"{city} {query}"
                    posts = await self.scraper.search_subreddit(sub, full_query, limit=10)
                    for post in posts:
                        if post.id not in seen_ids:
                            post.category = category
                            post.relevance_score = self.scraper.calculate_relevance(post, city, category)
                            all_posts.append(post)
                            seen_ids.add(post.id)

        # Global search for city
        print("\nGlobal Reddit search...")
        global_posts = await self.scraper.search_global(f"{city} travel tips", limit=25)
        for post in global_posts:
            if post.id not in seen_ids:
                post.category = "general"
                post.relevance_score = self.scraper.calculate_relevance(post, city, "general")
                all_posts.append(post)
                seen_ids.add(post.id)

        # Organize by category
        data.posts = all_posts
        for post in all_posts:
            if post.category not in data.categories:
                data.categories[post.category] = []
            data.categories[post.category].append(post)

        # Sort each category by relevance
        for category in data.categories:
            data.categories[category].sort(key=lambda x: x.relevance_score, reverse=True)

        print(f"\nCollected {len(all_posts)} posts across {len(data.categories)} categories")
        return data


async def collect_city_intelligence(city: str, output_file: Optional[str] = None) -> CityRedditData:
    """
    Main function to collect city intelligence from Reddit.

    Args:
        city: Name of the city to research
        output_file: Optional path to save JSON output

    Returns:
        CityRedditData object with collected information
    """
    scraper = RedditScraper(rate_limit_delay=2.0)
    collector = CityIntelligenceCollector(scraper)

    try:
        data = await collector.collect_city_data(city)

        if output_file:
            with open(output_file, 'w') as f:
                json.dump(data.to_dict(), f, indent=2)
            print(f"\nSaved to {output_file}")

        return data
    finally:
        await scraper.close()


# CLI usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python reddit_scraper.py <city_name> [output_file]")
        sys.exit(1)

    city = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else f"city_intelligence/cities/{city.lower().replace(' ', '_')}_reddit.json"

    asyncio.run(collect_city_intelligence(city, output_file))
