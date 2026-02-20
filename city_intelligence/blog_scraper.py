"""
Travel Blog Scraper for City Intelligence.
Crawls curated travel blogs from TRAVEL_RESOURCES.md for city-specific content.

Uses DuckDuckGo HTML search with site: filters to find relevant articles
from trusted travel blog sources, then extracts titles, URLs, and snippets.
"""
import asyncio
import httpx
import re
import json
import logging
from dataclasses import dataclass, field
from typing import Optional
from html.parser import HTMLParser
from urllib.parse import quote_plus, unquote, urlparse, parse_qs
from datetime import datetime

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Blog source definitions from TRAVEL_RESOURCES.md Section 2
# ---------------------------------------------------------------------------

BLOG_SOURCES = [
    {"name": "Atlas Obscura", "domain": "atlasobscura.com", "category": "hidden_gems"},
    {"name": "Lonely Planet", "domain": "lonelyplanet.com", "category": "general"},
    {"name": "Rick Steves", "domain": "ricksteves.com", "category": "general"},
    {"name": "Culture Trip", "domain": "theculturetrip.com", "category": "culture"},
    {"name": "Eater", "domain": "eater.com", "category": "food"},
    {"name": "Nomadic Matt", "domain": "nomadicmatt.com", "category": "budget"},
    {"name": "Spotted by Locals", "domain": "spottedbylocals.com", "category": "local_tips"},
    {"name": "Trekaroo", "domain": "trekaroo.com", "category": "family"},
]

# User-Agent that mimics a standard browser to avoid immediate blocking
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# DuckDuckGo HTML search endpoint (more scraping-friendly than Google)
DDG_SEARCH_URL = "https://html.duckduckgo.com/html/"

# Rate limiting between requests (seconds)
DEFAULT_RATE_LIMIT = 2.5

# Maximum number of articles to fetch full content for per source
MAX_FULL_FETCH_PER_SOURCE = 3

# Request timeout in seconds
REQUEST_TIMEOUT = 30.0


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class BlogArticle:
    """Represents a single scraped blog article."""
    title: str
    url: str
    snippet: str  # First ~300 chars of article text
    source: str  # Blog name (e.g., "Atlas Obscura")
    category: str  # e.g., "hidden_gems", "food", "budget"

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet[:300] if self.snippet else "",
            "source": self.source,
            "category": self.category,
        }


@dataclass
class CityBlogData:
    """Container for all blog data collected about a city."""
    city_name: str
    country: str = ""
    collected_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    articles: list[BlogArticle] = field(default_factory=list)
    sources_searched: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "city_name": self.city_name,
            "country": self.country,
            "collected_at": self.collected_at,
            "total_articles": len(self.articles),
            "sources_searched": self.sources_searched,
            "articles_by_category": self._group_by_category(),
            "articles_by_source": self._group_by_source(),
            "articles": [a.to_dict() for a in self.articles],
        }

    def _group_by_source(self) -> dict:
        groups: dict[str, list[dict]] = {}
        for a in self.articles:
            if a.source not in groups:
                groups[a.source] = []
            groups[a.source].append(a.to_dict())
        return groups

    def _group_by_category(self) -> dict:
        groups: dict[str, list[dict]] = {}
        for a in self.articles:
            if a.category not in groups:
                groups[a.category] = []
            groups[a.category].append(a.to_dict())
        return groups


# ---------------------------------------------------------------------------
# HTML parsing utilities
# ---------------------------------------------------------------------------

class HTMLTextExtractor(HTMLParser):
    """
    Strips HTML tags and extracts visible text content.
    Ignores script, style, and other non-visible elements.
    """

    SKIP_TAGS = frozenset({"script", "style", "noscript", "svg", "head", "nav", "footer", "header"})

    def __init__(self) -> None:
        super().__init__()
        self._pieces: list[str] = []
        self._skip_depth: int = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        if tag.lower() in self.SKIP_TAGS:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in self.SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0:
            cleaned = data.strip()
            if cleaned:
                self._pieces.append(cleaned)

    def get_text(self) -> str:
        """Return extracted text with pieces joined by spaces, collapsed whitespace."""
        raw = " ".join(self._pieces)
        # Collapse multiple whitespace chars into a single space
        return re.sub(r"\s+", " ", raw).strip()


def extract_text_from_html(html: str) -> str:
    """Extract visible text from an HTML string."""
    extractor = HTMLTextExtractor()
    try:
        extractor.feed(html)
    except Exception:
        pass
    return extractor.get_text()


class DuckDuckGoResultParser(HTMLParser):
    """
    Parses the DuckDuckGo HTML search results page to extract
    result titles, URLs, and text snippets.

    DuckDuckGo HTML results structure:
    - Each result is in a div with class "result" or "result results_links"
    - Title is in <a class="result__a"> with the URL as href
    - Snippet is in <a class="result__snippet">
    """

    def __init__(self) -> None:
        super().__init__()
        self.results: list[dict] = []
        self._current_result: Optional[dict] = None
        self._in_title: bool = False
        self._in_snippet: bool = False
        self._text_buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        attr_dict = dict(attrs)
        class_val = attr_dict.get("class", "") or ""

        # Detect a result link (title)
        if tag == "a" and "result__a" in class_val:
            href = attr_dict.get("href", "")
            self._current_result = {
                "title": "",
                "url": self._extract_real_url(href),
                "snippet": "",
            }
            self._in_title = True
            self._text_buffer = []

        # Detect snippet
        elif tag == "a" and "result__snippet" in class_val:
            self._in_snippet = True
            self._text_buffer = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "a":
            if self._in_title and self._current_result is not None:
                self._current_result["title"] = " ".join(self._text_buffer).strip()
                self._in_title = False
                self._text_buffer = []
            elif self._in_snippet and self._current_result is not None:
                self._current_result["snippet"] = " ".join(self._text_buffer).strip()
                self._in_snippet = False
                self._text_buffer = []
                # Snippet marks end of a result; save it
                if self._current_result.get("title") and self._current_result.get("url"):
                    self.results.append(self._current_result)
                self._current_result = None

    def handle_data(self, data: str) -> None:
        if self._in_title or self._in_snippet:
            cleaned = data.strip()
            if cleaned:
                self._text_buffer.append(cleaned)

    @staticmethod
    def _extract_real_url(ddg_href: str) -> str:
        """
        DuckDuckGo wraps result URLs through a redirect:
        //duckduckgo.com/l/?uddg=<encoded_real_url>&rut=...
        Extract the actual destination URL.
        """
        if not ddg_href:
            return ""

        # Direct URL (no redirect wrapper)
        if ddg_href.startswith("http://") or ddg_href.startswith("https://"):
            return ddg_href

        # Handle //duckduckgo.com/l/?uddg=... redirect
        if "duckduckgo.com/l/" in ddg_href:
            try:
                # Ensure it has a scheme for urlparse
                full_url = ddg_href if ddg_href.startswith("http") else "https:" + ddg_href
                parsed = urlparse(full_url)
                params = parse_qs(parsed.query)
                uddg_list = params.get("uddg", [])
                if uddg_list:
                    return unquote(uddg_list[0])
            except Exception:
                pass

        # Fallback: try to decode as-is
        return unquote(ddg_href)


def parse_ddg_results(html: str) -> list[dict]:
    """
    Parse DuckDuckGo HTML search page and return a list of results.
    Each result is a dict with keys: title, url, snippet.
    """
    parser = DuckDuckGoResultParser()
    try:
        parser.feed(html)
    except Exception as e:
        logger.warning("Failed to parse DuckDuckGo results: %s", e)
    return parser.results


# ---------------------------------------------------------------------------
# Blog scraper
# ---------------------------------------------------------------------------

class BlogScraper:
    """
    Scrapes travel blog articles for a given city using DuckDuckGo search.
    Uses site: filters to target specific blog domains.
    """

    def __init__(self, rate_limit_delay: float = DEFAULT_RATE_LIMIT) -> None:
        self.rate_limit_delay = rate_limit_delay
        self.client = httpx.AsyncClient(
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
            follow_redirects=True,
        )

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self.client.aclose()

    async def _rate_limit(self) -> None:
        """Sleep to respect rate limits."""
        await asyncio.sleep(self.rate_limit_delay)

    async def _fetch_html(self, url: str) -> Optional[str]:
        """
        Fetch a page and return its HTML body, or None on failure.
        Includes rate limiting between requests.
        """
        await self._rate_limit()
        try:
            response = await self.client.get(url)
            if response.status_code == 200:
                return response.text
            else:
                logger.info("HTTP %d for %s", response.status_code, url[:120])
                return None
        except httpx.TimeoutException:
            logger.warning("Timeout fetching %s", url[:120])
            return None
        except Exception as e:
            logger.warning("Error fetching %s: %s", url[:120], e)
            return None

    def _build_search_query(self, city: str, country: str, domain: str) -> str:
        """
        Build a DuckDuckGo search query string.
        Example: site:atlasobscura.com "Florence" "Italy" travel
        """
        parts = [f"site:{domain}"]

        # Quote the city name for exact matching
        parts.append(f'"{city}"')

        # Include country for disambiguation (important for cities like Florence, Paris)
        if country:
            parts.append(f'"{country}"')

        parts.append("travel")
        return " ".join(parts)

    async def search_blog_source(
        self,
        city: str,
        country: str,
        source: dict,
    ) -> list[BlogArticle]:
        """
        Search a single blog source via DuckDuckGo and return found articles.

        Args:
            city: City name (e.g., "Florence")
            country: Country name (e.g., "Italy")
            source: Blog source dict with 'name', 'domain', 'category'

        Returns:
            List of BlogArticle objects found for this source.
        """
        domain = source["domain"]
        name = source["name"]
        category = source["category"]

        query = self._build_search_query(city, country, domain)
        encoded_query = quote_plus(query)
        search_url = f"{DDG_SEARCH_URL}?q={encoded_query}"

        logger.info("Searching %s: %s", name, query)
        print(f"  Searching {name} (site:{domain})...")

        html = await self._fetch_html(search_url)
        if not html:
            logger.info("No results from DuckDuckGo for %s", name)
            return []

        raw_results = parse_ddg_results(html)
        if not raw_results:
            logger.info("No parsed results for %s", name)
            return []

        # Filter results to only include URLs that actually belong to the target domain
        filtered = []
        for r in raw_results:
            url = r.get("url", "")
            if domain.lower() in url.lower():
                filtered.append(r)

        logger.info("Found %d results for %s (filtered from %d)", len(filtered), name, len(raw_results))

        # Convert to BlogArticle objects
        articles = []
        seen_urls: set[str] = set()

        for result in filtered:
            url = result["url"]
            if url in seen_urls:
                continue
            seen_urls.add(url)

            title = result.get("title", "").strip()
            snippet = result.get("snippet", "").strip()

            # Clean up title: remove site name suffix if present
            title = self._clean_title(title, name)

            if not title:
                continue

            articles.append(BlogArticle(
                title=title,
                url=url,
                snippet=snippet,
                source=name,
                category=category,
            ))

        # Optionally enrich the top articles with better snippets from the actual pages
        enriched = await self._enrich_articles(articles[:MAX_FULL_FETCH_PER_SOURCE])
        # Replace enriched articles in the list
        for i, enriched_article in enumerate(enriched):
            if i < len(articles):
                articles[i] = enriched_article

        print(f"    Found {len(articles)} article(s) from {name}")
        return articles

    async def _enrich_articles(self, articles: list[BlogArticle]) -> list[BlogArticle]:
        """
        Fetch the actual article pages for a list of articles and extract
        better text snippets from the page body.
        """
        enriched = []
        for article in articles:
            page_html = await self._fetch_html(article.url)
            if page_html:
                body_text = extract_text_from_html(page_html)
                if body_text and len(body_text) > len(article.snippet):
                    # Extract a meaningful snippet from the body
                    snippet = self._extract_snippet(body_text, article.title)
                    if snippet:
                        article.snippet = snippet
            enriched.append(article)
        return enriched

    @staticmethod
    def _extract_snippet(body_text: str, title: str) -> str:
        """
        Extract a relevant ~300-character snippet from article body text.
        Tries to find content after the title or early in the body,
        skipping navigation/boilerplate that often appears at the start.
        """
        if not body_text:
            return ""

        # Try to find content near the title text
        title_lower = title.lower().strip()
        body_lower = body_text.lower()

        start_idx = 0
        if title_lower and title_lower in body_lower:
            title_pos = body_lower.index(title_lower)
            # Start after the title
            start_idx = title_pos + len(title_lower)

        # If we didn't find the title or it's at the very beginning,
        # skip the first chunk which is often navigation boilerplate
        if start_idx < 50:
            # Try to skip past common boilerplate by finding the first
            # paragraph-length chunk of text
            sentences = re.split(r"(?<=[.!?])\s+", body_text[200:])
            if len(sentences) >= 2:
                # Join first few sentences for the snippet
                candidate = " ".join(sentences[:3]).strip()
                if len(candidate) > 50:
                    return candidate[:300]

        # Extract from the determined start position
        text_from_start = body_text[start_idx:].strip()

        # Skip very short fragments (likely headings/nav)
        words = text_from_start.split()
        if len(words) < 10 and start_idx < len(body_text) - 500:
            # Try a bit further in
            text_from_start = body_text[start_idx + 100:].strip()

        # Take first ~300 chars, ending at a word boundary
        if len(text_from_start) > 300:
            cut = text_from_start[:300]
            last_space = cut.rfind(" ")
            if last_space > 200:
                cut = cut[:last_space]
            return cut.strip() + "..."
        return text_from_start.strip()

    @staticmethod
    def _clean_title(title: str, source_name: str) -> str:
        """
        Clean up an article title by removing common suffixes like
        '| Atlas Obscura', '- Lonely Planet', etc.
        """
        if not title:
            return title

        # Common separators used by blogs to append their name
        separators = [" | ", " - ", " -- ", " \u2013 ", " \u2014 "]
        for sep in separators:
            if sep in title:
                parts = title.split(sep)
                # Check if the last part is the source name (or close to it)
                last_part = parts[-1].strip().lower()
                source_lower = source_name.lower()
                # Also check against common brand variations
                if (source_lower in last_part
                        or last_part in source_lower
                        or last_part in {"atlas obscura", "lonely planet", "rick steves",
                                         "culture trip", "theculturetrip", "eater",
                                         "nomadic matt", "spotted by locals",
                                         "trekaroo", "nomadicmatt.com"}):
                    title = sep.join(parts[:-1]).strip()
                    break

        return title


# ---------------------------------------------------------------------------
# Main collection function
# ---------------------------------------------------------------------------

async def collect_blog_intelligence(
    city: str,
    country: str = "",
    output_file: Optional[str] = None,
    sources: Optional[list[dict]] = None,
    rate_limit_delay: float = DEFAULT_RATE_LIMIT,
    fetch_full_articles: bool = True,
) -> CityBlogData:
    """
    Main function to collect travel blog intelligence for a city.

    Searches curated blog sources from TRAVEL_RESOURCES.md using DuckDuckGo,
    extracts article titles, URLs, and text snippets, then groups results
    by source and category.

    Args:
        city: Name of the city to research (e.g., "Florence").
        country: Country name for disambiguation (e.g., "Italy").
                 If empty, auto-detection is attempted.
        output_file: Optional file path to save JSON output.
        sources: Optional override list of blog source dicts.
                 Defaults to BLOG_SOURCES.
        rate_limit_delay: Seconds to wait between HTTP requests.
        fetch_full_articles: Whether to fetch actual article pages
                            for richer snippets.

    Returns:
        CityBlogData object with all collected articles.
    """
    if not country:
        country = _guess_country(city)

    blog_sources = sources if sources is not None else BLOG_SOURCES

    print(f"\n{'='*60}")
    print(f"Collecting blog intelligence for: {city}, {country}")
    print(f"Searching {len(blog_sources)} blog sources via DuckDuckGo")
    print(f"{'='*60}")

    scraper = BlogScraper(rate_limit_delay=rate_limit_delay)

    # Temporarily disable full article fetching if requested
    if not fetch_full_articles:
        original_max = MAX_FULL_FETCH_PER_SOURCE
        # We use a module-level constant, so we patch the scraper method instead
        scraper._enrich_articles = _noop_enrich  # type: ignore[assignment]

    data = CityBlogData(city_name=city, country=country)

    try:
        for source in blog_sources:
            data.sources_searched.append(source["name"])

            try:
                articles = await scraper.search_blog_source(city, country, source)
                data.articles.extend(articles)
            except Exception as e:
                logger.error("Error searching %s: %s", source["name"], e)
                print(f"    Error searching {source['name']}: {e}")

        # Deduplicate articles by URL
        seen_urls: set[str] = set()
        unique_articles: list[BlogArticle] = []
        for article in data.articles:
            normalized_url = article.url.rstrip("/").lower()
            if normalized_url not in seen_urls:
                seen_urls.add(normalized_url)
                unique_articles.append(article)
        data.articles = unique_articles

        print(f"\n{'='*60}")
        print(f"Results: {len(data.articles)} unique articles from {len(data.sources_searched)} sources")

        # Print summary by category
        category_counts: dict[str, int] = {}
        for article in data.articles:
            category_counts[article.category] = category_counts.get(article.category, 0) + 1
        for cat, count in sorted(category_counts.items()):
            print(f"  {cat}: {count} articles")
        print(f"{'='*60}\n")

        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data.to_dict(), f, indent=2, ensure_ascii=False)
            print(f"Saved to {output_file}")

        return data

    finally:
        await scraper.close()


async def _noop_enrich(articles: list[BlogArticle]) -> list[BlogArticle]:
    """No-op enrichment function used when fetch_full_articles is False."""
    return articles


# ---------------------------------------------------------------------------
# Country auto-detection (mirrors reddit_scraper.py)
# ---------------------------------------------------------------------------

def _guess_country(city: str) -> str:
    """Auto-detect country from known city names."""
    city_country_map = {
        "rome": "Italy", "florence": "Italy", "venice": "Italy",
        "milan": "Italy", "naples": "Italy", "amalfi": "Italy",
        "bologna": "Italy", "siena": "Italy", "verona": "Italy",
        "paris": "France", "nice": "France", "lyon": "France",
        "bordeaux": "France", "marseille": "France", "strasbourg": "France",
        "barcelona": "Spain", "madrid": "Spain", "seville": "Spain",
        "granada": "Spain", "valencia": "Spain", "malaga": "Spain",
        "tokyo": "Japan", "kyoto": "Japan", "osaka": "Japan",
        "hiroshima": "Japan", "nara": "Japan", "fukuoka": "Japan",
        "london": "UK", "edinburgh": "UK", "bath": "UK",
        "oxford": "UK", "cambridge": "UK", "york": "UK",
        "berlin": "Germany", "munich": "Germany", "hamburg": "Germany",
        "cologne": "Germany", "dresden": "Germany",
        "amsterdam": "Netherlands", "rotterdam": "Netherlands",
        "prague": "Czech Republic", "vienna": "Austria",
        "salzburg": "Austria", "lisbon": "Portugal", "porto": "Portugal",
        "athens": "Greece", "santorini": "Greece", "crete": "Greece",
        "bangkok": "Thailand", "chiang mai": "Thailand",
        "delhi": "India", "mumbai": "India", "jaipur": "India",
        "istanbul": "Turkey", "dublin": "Ireland",
        "copenhagen": "Denmark", "stockholm": "Sweden",
        "oslo": "Norway", "helsinki": "Finland",
        "budapest": "Hungary", "krakow": "Poland", "warsaw": "Poland",
        "zurich": "Switzerland", "geneva": "Switzerland",
        "brussels": "Belgium", "bruges": "Belgium",
    }
    return city_country_map.get(city.lower(), "")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    if len(sys.argv) < 2:
        print("Usage: python blog_scraper.py <city_name> [country] [output_file.json]")
        print()
        print("Examples:")
        print("  python blog_scraper.py Florence Italy")
        print("  python blog_scraper.py Florence Italy florence_blogs.json")
        print("  python blog_scraper.py Tokyo")
        sys.exit(1)

    city_arg = sys.argv[1]

    # Determine country and output file from arguments
    country_arg = ""
    output_arg = None

    if len(sys.argv) > 2:
        # If last argument ends with .json, it's the output file
        if sys.argv[-1].endswith(".json"):
            output_arg = sys.argv[-1]
            # If there's a middle argument, it's the country
            if len(sys.argv) > 3:
                country_arg = sys.argv[2]
        else:
            country_arg = sys.argv[2]

    # Default output file
    if output_arg is None:
        safe_name = city_arg.lower().replace(" ", "_")
        output_arg = f"city_intelligence/cities/{safe_name}_blogs.json"

    asyncio.run(collect_blog_intelligence(city_arg, country_arg, output_arg))
