"""
Multi-source web POI crawler.

Auto-discovers travel content from the open web, editorial sources,
existing blog sources, and TripAdvisor search snippets. Extracts
individual POI entities from article text using regex-based patterns.

Supports DuckDuckGo (always free) and Google Custom Search (optional).
"""
import asyncio
import logging
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List, Optional
from urllib.parse import quote_plus, urlparse

import httpx

# Reuse utilities from city_intelligence/blog_scraper
_ci_dir = str(Path(__file__).resolve().parents[3] / "city_intelligence")
if _ci_dir not in sys.path:
    sys.path.insert(0, _ci_dir)

from blog_scraper import (
    BLOG_SOURCES,
    DDG_SEARCH_URL,
    HEADERS,
    extract_text_from_html,
    parse_ddg_results,
)
from app.services.data_ingestion.crawl_to_poi_converter import _TA_SUFFIX_PATTERN

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Source definitions
# ---------------------------------------------------------------------------

EDITORIAL_SOURCES = [
    {"name": "WikiVoyage", "domain": "wikivoyage.org", "category": "wiki"},
    {"name": "Timeout", "domain": "timeout.com", "category": "editorial"},
    {"name": "Conde Nast Traveler", "domain": "cntraveler.com", "category": "editorial"},
    {"name": "Travel+Leisure", "domain": "travelandleisure.com", "category": "editorial"},
    {"name": "Yelp", "domain": "yelp.com", "category": "review"},
]

OPEN_WEB_QUERIES = [
    "best restaurants in {city}",
    "things to do in {city}",
    "hidden gems {city}",
    "must see attractions {city}",
    "best cafes {city}",
    "street food {city}",
    "romantic spots {city}",
    "family friendly activities {city}",
    "nightlife {city}",
    "outdoor activities {city}",
]

TRIPADVISOR_QUERIES = [
    "site:tripadvisor.com {city} things to do",
    "site:tripadvisor.com {city} restaurants",
    "site:tripadvisor.com {city} hidden gems",
    "site:tripadvisor.com {city} attractions",
    "site:tripadvisor.com {city} best food",
    "site:tripadvisor.com {city} nightlife",
    "site:tripadvisor.com {city} shopping",
    "site:tripadvisor.com {city} cafes",
]

SOURCE_BOOSTS = {
    "wikivoyage.org": {"score_cultural": 0.10, "score_solo": 0.10},
    "timeout.com": {"score_nightlife": 0.15, "score_friends": 0.10},
    "cntraveler.com": {"score_couple": 0.10, "score_romantic": 0.10},
    "travelandleisure.com": {"score_relaxation": 0.10, "score_couple": 0.10},
    "yelp.com": {"score_foodie": 0.15},
    "atlasobscura.com": {"score_adventure": 0.15},
    "eater.com": {"score_foodie": 0.20},
    "trekaroo.com": {"score_family": 0.15, "score_kids": 0.15},
}

# Direct URL patterns for known sources (fallback when search is blocked)
# {city_slug} = lowercase, hyphenated city name (e.g., "rome", "new-york")
DIRECT_URL_PATTERNS = {
    "wikivoyage.org": [
        "https://en.wikivoyage.org/wiki/{city}",
    ],
    "timeout.com": [
        "https://www.timeout.com/{city_slug}/things-to-do/best-things-to-do-in-{city_slug}",
        "https://www.timeout.com/{city_slug}/restaurants/best-restaurants-in-{city_slug}",
        "https://www.timeout.com/{city_slug}/things-to-do/free-things-to-do-in-{city_slug}",
    ],
    "lonelyplanet.com": [
        "https://www.lonelyplanet.com/{country_slug}/{city_slug}/top-things-to-do",
        "https://www.lonelyplanet.com/{country_slug}/{city_slug}/restaurants",
    ],
    "cntraveler.com": [
        "https://www.cntraveler.com/gallery/best-things-to-do-in-{city_slug}",
        "https://www.cntraveler.com/gallery/best-restaurants-in-{city_slug}",
    ],
    "atlasobscura.com": [
        "https://www.atlasobscura.com/things-to-do/{city_slug}",
    ],
    "eater.com": [
        "https://www.eater.com/maps/best-restaurants-{city_slug}",
    ],
}

# Rate limit and fetch caps
RATE_LIMIT_SECONDS = 2.5
MAX_PAGES_TO_FETCH = 50
REQUEST_TIMEOUT = 30.0

# Google Custom Search endpoint
GOOGLE_SEARCH_URL = "https://www.googleapis.com/customsearch/v1"

# Category keyword mapping for POI extraction
CATEGORY_KEYWORDS = {
    "restaurant": [
        "restaurant", "trattoria", "bistro", "eatery", "dining", "pizzeria",
        "osteria", "brasserie", "taverna", "izakaya", "ramen", "sushi",
        "steakhouse", "seafood", "brunch", "diner",
    ],
    "cafe": [
        "cafe", "coffee", "bakery", "patisserie", "pastry", "tea house",
        "gelateria", "gelato",
    ],
    "bar": [
        "bar", "pub", "cocktail", "wine bar", "speakeasy", "brewery",
        "taproom", "rooftop bar",
    ],
    "attraction": [
        "museum", "gallery", "palace", "castle", "cathedral", "basilica",
        "temple", "shrine", "monument", "ruins", "forum", "tower",
        "bridge", "square", "piazza", "plaza", "abbey", "church",
        "mosque", "synagogue", "library", "opera", "theater", "theatre",
    ],
    "park": [
        "park", "garden", "botanical", "beach", "lake", "river walk",
        "promenade", "trail", "viewpoint", "overlook",
    ],
    "shopping": [
        "market", "bazaar", "mall", "boutique", "shop", "store",
        "flea market", "souk",
    ],
    "nightlife": [
        "club", "nightclub", "disco", "lounge", "cabaret", "flamenco",
        "jazz club", "live music",
    ],
    "activity": [
        "tour", "cooking class", "boat ride", "cruise", "excursion",
        "workshop", "spa", "onsen", "thermal bath",
    ],
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class DiscoveredPage:
    url: str
    title: str
    snippet: str
    source_domain: str
    source_category: str  # "editorial" | "review" | "wiki" | "web" | "blog"
    search_provider: str  # "duckduckgo" | "google" | "user_provided"
    rating: Optional[float] = None
    review_count: Optional[int] = None


@dataclass
class ExtractedPOI:
    name: str
    description: str
    category: str  # "attraction" | "restaurant" | "shopping" | etc.
    subcategory: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    price_signal: Optional[str] = None
    source_url: str = ""
    source_domain: str = ""


# ---------------------------------------------------------------------------
# SearchClient — DuckDuckGo + optional Google Custom Search
# ---------------------------------------------------------------------------

class SearchClient:
    """Searches DuckDuckGo (always) and Google Custom Search (if configured)."""

    def __init__(
        self,
        google_api_key: str = "",
        google_cx: str = "",
        rate_limit: float = RATE_LIMIT_SECONDS,
    ):
        self.google_api_key = google_api_key
        self.google_cx = google_cx
        self.rate_limit = rate_limit
        self.client = httpx.AsyncClient(
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
            follow_redirects=True,
        )

    async def close(self):
        await self.client.aclose()

    async def _wait(self):
        await asyncio.sleep(self.rate_limit)

    # -- DuckDuckGo ---

    async def search_ddg(self, query: str) -> List[DiscoveredPage]:
        """Search DuckDuckGo using the duckduckgo-search library (handles CAPTCHAs)."""
        await self._wait()
        try:
            raw = await asyncio.to_thread(self._ddg_search_sync, query)
        except Exception as e:
            logger.warning("DDG search error for '%s': %s", query[:80], e)
            return []

        pages = []
        for r in raw:
            result_url = r.get("href", "") or r.get("url", "")
            if not result_url:
                continue
            domain = urlparse(result_url).netloc.lower().replace("www.", "")
            pages.append(DiscoveredPage(
                url=result_url,
                title=r.get("title", ""),
                snippet=r.get("body", "") or r.get("snippet", ""),
                source_domain=domain,
                source_category=_classify_domain(domain),
                search_provider="duckduckgo",
            ))
        return pages

    @staticmethod
    def _ddg_search_sync(query: str) -> list:
        """Synchronous DDG search using duckduckgo-search library."""
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=10))
            return results
        except Exception as e:
            logger.warning("duckduckgo-search failed for '%s': %s", query[:80], e)
            return []

    # -- Google Custom Search ---

    async def search_google(self, query: str) -> List[DiscoveredPage]:
        """Search Google Custom Search JSON API. Returns empty if not configured."""
        if not self.google_api_key or not self.google_cx:
            return []
        await self._wait()
        try:
            resp = await self.client.get(
                GOOGLE_SEARCH_URL,
                params={
                    "key": self.google_api_key,
                    "cx": self.google_cx,
                    "q": query,
                    "num": 10,
                },
            )
            if resp.status_code != 200:
                logger.info("Google search HTTP %d for: %s", resp.status_code, query[:80])
                return []
            data = resp.json()
        except Exception as e:
            logger.warning("Google search error for '%s': %s", query[:80], e)
            return []

        pages = []
        for item in data.get("items", []):
            result_url = item.get("link", "")
            if not result_url:
                continue
            domain = urlparse(result_url).netloc.lower().replace("www.", "")
            pages.append(DiscoveredPage(
                url=result_url,
                title=item.get("title", ""),
                snippet=item.get("snippet", ""),
                source_domain=domain,
                source_category=_classify_domain(domain),
                search_provider="google",
            ))
        return pages

    # -- Combined ---

    async def search_all(self, query: str) -> List[DiscoveredPage]:
        """Search DDG + Google (if configured), deduplicate by URL."""
        ddg_results = await self.search_ddg(query)
        google_results = await self.search_google(query)

        seen_urls: set = set()
        combined: List[DiscoveredPage] = []
        for page in ddg_results + google_results:
            norm = page.url.rstrip("/").lower()
            if norm not in seen_urls:
                seen_urls.add(norm)
                combined.append(page)
        return combined


def _classify_domain(domain: str) -> str:
    """Classify a domain into a source category."""
    editorial_domains = {s["domain"] for s in EDITORIAL_SOURCES}
    blog_domains = {s["domain"] for s in BLOG_SOURCES}
    if "tripadvisor" in domain:
        return "review"
    if any(d in domain for d in editorial_domains):
        return "editorial"
    if any(d in domain for d in blog_domains):
        return "blog"
    if "wikivoyage" in domain:
        return "wiki"
    if "yelp" in domain:
        return "review"
    return "web"


# ---------------------------------------------------------------------------
# POIEntityExtractor — extracts individual POIs from article text
# ---------------------------------------------------------------------------

# Regex patterns for POI extraction
_NUMBERED_LIST_RE = re.compile(
    r"^\d+[\.\)]\s+(.{3,80}?)\s*[-\u2013\u2014:.]\s*(.{10,500})",
    re.MULTILINE,
)
_BOLD_ENTRY_RE = re.compile(
    r"\*\*([^*]{3,80})\*\*\s*[-\u2013\u2014:.]\s*(.{10,500})"
)
_HEADING_RE = re.compile(
    r"#{2,3}\s+(.+?)(?:\n)",
)
_PROPER_NOUN_RE = re.compile(
    r"(?:^|\.\s+)([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,5})"
)

# Rating/review patterns for TripAdvisor snippets
_RATING_RE = re.compile(r"(\d+\.?\d*)\s*(?:of|out of)\s*5|(\d+\.?\d*)\s*/\s*5|rating[:\s]*(\d+\.?\d*)")
_REVIEW_COUNT_RE = re.compile(r"([\d,]+)\s*review", re.IGNORECASE)


class POIEntityExtractor:
    """Extracts individual POI entities from article body text."""

    def extract_pois_from_text(
        self,
        text: str,
        source_url: str = "",
        source_domain: str = "",
    ) -> List[ExtractedPOI]:
        """
        Extract POI entities from text using multiple regex patterns.
        Returns deduplicated list of ExtractedPOI.
        """
        if not text or len(text.strip()) < 20:
            return []

        pois: List[ExtractedPOI] = []
        seen_names: set = set()

        def _add_poi(name: str, desc: str):
            name = _clean_poi_name(name)
            if not name or len(name) < 3:
                return
            norm = _normalize_name(name)
            if norm in seen_names or len(norm) < 3:
                return
            # Skip things that look like generic phrases, not POI names
            if _is_generic_phrase(name):
                return
            seen_names.add(norm)
            category = self._guess_category(name, desc)
            pois.append(ExtractedPOI(
                name=name,
                description=desc.strip()[:500] if desc else "",
                category=category,
                source_url=source_url,
                source_domain=source_domain,
            ))

        # Pass 1: Numbered lists ("1. Colosseum - The iconic ...")
        for m in _NUMBERED_LIST_RE.finditer(text):
            _add_poi(m.group(1), m.group(2))

        # Pass 2: Bold entries ("**Trattoria da Mario** — ...")
        for m in _BOLD_ENTRY_RE.finditer(text):
            _add_poi(m.group(1), m.group(2))

        # Pass 3: Markdown headings followed by text
        for m in _HEADING_RE.finditer(text):
            heading = m.group(1).strip()
            # Get the paragraph after the heading
            start = m.end()
            end = min(start + 500, len(text))
            following = text[start:end].strip()
            # Take first sentence as description
            sent_end = re.search(r"[.!?]\s", following)
            desc = following[:sent_end.end()] if sent_end else following[:300]
            _add_poi(heading, desc)

        # Pass 4: Proper noun heuristic (fallback) — only if few POIs found
        if len(pois) < 3:
            all_category_kws = set()
            for kws in CATEGORY_KEYWORDS.values():
                all_category_kws.update(kws)

            for m in _PROPER_NOUN_RE.finditer(text):
                name = m.group(1).strip()
                # Check if it's near a category keyword
                context_start = max(0, m.start() - 100)
                context_end = min(len(text), m.end() + 200)
                context = text[context_start:context_end].lower()
                if any(kw in context for kw in all_category_kws):
                    _add_poi(name, context[100:300])

        return pois

    def extract_pois_from_snippet(
        self,
        title: str,
        snippet: str,
        source_url: str = "",
        source_domain: str = "",
        rating: Optional[float] = None,
        review_count: Optional[int] = None,
    ) -> List[ExtractedPOI]:
        """
        Extract POI from a search result snippet (e.g. TripAdvisor).
        Typically yields 0 or 1 POI per snippet.
        """
        if not title:
            return []

        # Clean TripAdvisor suffixes
        clean_title = _TA_SUFFIX_PATTERN.sub("", title).strip()
        if not clean_title:
            return []

        # Skip aggregate pages
        if re.search(r"THE \d+ BEST|Top \d+|Things to Do", clean_title, re.IGNORECASE):
            return []

        # Try to extract rating/review from snippet if not provided
        if rating is None and snippet:
            rating = _extract_rating(snippet)
        if review_count is None and snippet:
            review_count = _extract_review_count(snippet)

        category = self._guess_category(clean_title, snippet or "")

        return [ExtractedPOI(
            name=clean_title,
            description=(snippet or "").strip()[:500],
            category=category,
            rating=rating,
            review_count=review_count,
            source_url=source_url,
            source_domain=source_domain,
        )]

    @staticmethod
    def _guess_category(name: str, description: str) -> str:
        """Guess POI category from name and description keywords."""
        text = f"{name} {description}".lower()

        # Check each category's keywords
        scores = {}
        for cat, keywords in CATEGORY_KEYWORDS.items():
            for kw in keywords:
                if kw in text:
                    scores[cat] = scores.get(cat, 0) + 1

        if scores:
            return max(scores, key=scores.get)
        return "attraction"  # default


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clean_poi_name(name: str) -> str:
    """Clean up a raw extracted POI name."""
    name = name.strip().rstrip(".:,;")
    # Remove leading articles if they create noise ("The Colosseum The" -> "Colosseum")
    # Only strip trailing orphan words (common in truncated extractions)
    name = re.sub(r"\s+(?:The|A|An|And|Or|In|At|Of|For|To|Is|It|By)$", "", name, flags=re.IGNORECASE)
    # Remove leading "The " only if followed by a proper noun and the name is longish
    if re.match(r"^The\s+[A-Z]", name) and len(name) > 20:
        # Keep "The" for well-known names like "The Louvre" but strip for junk like "The Almost Corner"
        pass
    # Remove trailing numbers that are artifacts
    name = re.sub(r"\s+\d+$", "", name)
    return name.strip()


def _normalize_name(name: str) -> str:
    """Normalize a POI name for deduplication."""
    return re.sub(r"[^a-z0-9]", "", name.lower())


def _is_generic_phrase(name: str) -> bool:
    """Check if a name is too generic to be a real POI."""
    generic = {
        "things to do", "best restaurants", "top attractions", "getting there",
        "how to get", "where to stay", "when to visit", "travel tips",
        "what to eat", "what to see", "day trip", "quick tip",
        "pro tip", "good to know", "keep in mind", "related articles",
        "read more", "see also", "table of contents", "final thoughts",
        "the bottom line", "in conclusion", "understand", "get around",
        "get in", "buy", "eat", "drink", "sleep", "stay safe", "cope",
        "connect", "go next", "respect", "north centre", "south centre",
        "old rome", "about ciampino", "some italian",
    }
    lower = name.lower().strip()
    return lower in generic or len(lower) > 80


def _extract_rating(text: str) -> Optional[float]:
    """Extract a rating value from text."""
    m = _RATING_RE.search(text)
    if m:
        for g in m.groups():
            if g:
                try:
                    val = float(g)
                    if 0 <= val <= 5:
                        return val
                except ValueError:
                    pass
    return None


def _extract_review_count(text: str) -> Optional[int]:
    """Extract review count from text."""
    m = _REVIEW_COUNT_RE.search(text)
    if m:
        try:
            return int(m.group(1).replace(",", ""))
        except ValueError:
            pass
    return None


# ---------------------------------------------------------------------------
# WebPOICrawler — orchestrates discovery + extraction
# ---------------------------------------------------------------------------

class WebPOICrawler:
    """
    Crawls multiple web sources to discover and extract POIs for a city.

    Usage::

        crawler = WebPOICrawler()
        pois = await crawler.auto_crawl("Rome", "Italy")
        await crawler.close()
    """

    def __init__(
        self,
        google_api_key: str = "",
        google_cx: str = "",
        rate_limit: float = RATE_LIMIT_SECONDS,
    ):
        self.search = SearchClient(google_api_key, google_cx, rate_limit)
        self.extractor = POIEntityExtractor()
        self.rate_limit = rate_limit

    async def close(self):
        await self.search.close()

    async def auto_crawl(
        self,
        city: str,
        country: str = "",
        include_open_web: bool = True,
        include_editorial: bool = True,
        include_blogs: bool = True,
        include_tripadvisor: bool = True,
        progress_callback: Optional[Callable] = None,
    ) -> List[ExtractedPOI]:
        """
        Auto-discover and extract POIs from multiple web sources.

        Args:
            city: City name.
            country: Country name for disambiguation.
            include_open_web: Search open web queries.
            include_editorial: Search editorial sources.
            include_blogs: Search blog sources.
            include_tripadvisor: Search TripAdvisor.
            progress_callback: Optional callback(stage, message) for progress.
        """
        def _progress(stage: str, msg: str):
            if progress_callback:
                progress_callback(stage, msg)

        # Phase 1: Discover pages
        _progress("discovering", f"Discovering pages for {city}...")
        pages = await self._discover_pages(
            city, country,
            include_open_web=include_open_web,
            include_editorial=include_editorial,
            include_blogs=include_blogs,
            include_tripadvisor=include_tripadvisor,
            progress_callback=progress_callback,
        )
        _progress("discovered", f"Discovered {len(pages)} pages for {city}")

        # Phase 2: Fetch & extract POIs
        all_pois: List[ExtractedPOI] = []
        pages_fetched = 0
        non_ta_pages = [p for p in pages if "tripadvisor" not in p.source_domain]
        ta_pages = [p for p in pages if "tripadvisor" in p.source_domain]

        # Handle TripAdvisor: snippet-only, no page fetch
        for page in ta_pages:
            pois = self._handle_tripadvisor(page)
            all_pois.extend(pois)

        _progress("extracting", f"Extracting POIs from {len(non_ta_pages)} pages...")

        # Fetch and extract from non-TA pages
        for page in non_ta_pages[:MAX_PAGES_TO_FETCH]:
            pois = await self._fetch_and_extract(page)
            all_pois.extend(pois)
            pages_fetched += 1
            if pages_fetched % 10 == 0:
                _progress("extracting", f"Fetched {pages_fetched}/{min(len(non_ta_pages), MAX_PAGES_TO_FETCH)} pages, {len(all_pois)} POIs so far")

        # Deduplicate
        all_pois = _dedup_pois(all_pois)
        _progress("done", f"Extracted {len(all_pois)} unique POIs from {pages_fetched} pages")

        return all_pois

    async def url_crawl(
        self,
        urls: List[str],
        city: str,
        country: str = "",
        progress_callback: Optional[Callable] = None,
    ) -> List[ExtractedPOI]:
        """
        Crawl user-provided URLs and extract POIs.

        Args:
            urls: List of URLs to crawl.
            city: City name for context.
            country: Country name.
            progress_callback: Optional callback(stage, message).
        """
        def _progress(stage: str, msg: str):
            if progress_callback:
                progress_callback(stage, msg)

        all_pois: List[ExtractedPOI] = []

        for i, url in enumerate(urls):
            _progress("extracting", f"Crawling URL {i+1}/{len(urls)}: {url[:80]}...")
            domain = urlparse(url).netloc.lower().replace("www.", "")
            page = DiscoveredPage(
                url=url,
                title="",
                snippet="",
                source_domain=domain,
                source_category="web",
                search_provider="user_provided",
            )
            pois = await self._fetch_and_extract(page)
            all_pois.extend(pois)

        all_pois = _dedup_pois(all_pois)
        _progress("done", f"Extracted {len(all_pois)} unique POIs from {len(urls)} URLs")
        return all_pois

    # -- Internal: page discovery ---

    async def _discover_pages(
        self,
        city: str,
        country: str,
        include_open_web: bool = True,
        include_editorial: bool = True,
        include_blogs: bool = True,
        include_tripadvisor: bool = True,
        progress_callback: Optional[Callable] = None,
    ) -> List[DiscoveredPage]:
        """Orchestrate all search queries and return discovered pages."""
        all_pages: List[DiscoveredPage] = []
        seen_urls: set = set()
        search_worked = False

        def _add_pages(pages: List[DiscoveredPage]):
            nonlocal search_worked
            for p in pages:
                norm = p.url.rstrip("/").lower()
                if norm not in seen_urls:
                    seen_urls.add(norm)
                    all_pages.append(p)
                    search_worked = True

        def _progress(stage: str, msg: str):
            if progress_callback:
                progress_callback(stage, msg)

        city_query = f"{city} {country}".strip() if country else city
        city_slug = city.lower().replace(" ", "-")
        country_slug = country.lower().replace(" ", "-") if country else ""

        # Open web queries
        if include_open_web:
            _progress("discovering", "Searching open web...")
            for query_template in OPEN_WEB_QUERIES:
                query = query_template.format(city=city_query)
                pages = await self.search.search_all(query)
                _add_pages(pages)

        # Editorial sources (search first, then direct URLs as fallback)
        if include_editorial:
            _progress("discovering", "Searching editorial sources...")
            for source in EDITORIAL_SOURCES:
                query = f"site:{source['domain']} {city_query} travel"
                pages = await self.search.search_ddg(query)
                for p in pages:
                    if source["domain"] in p.source_domain:
                        p.source_category = source["category"]
                _add_pages(pages)

        # Blog sources (search first, then direct URLs as fallback)
        if include_blogs:
            _progress("discovering", "Searching blog sources...")
            for source in BLOG_SOURCES:
                query = f"site:{source['domain']} {city_query} travel"
                pages = await self.search.search_ddg(query)
                for p in pages:
                    if source["domain"] in p.source_domain:
                        p.source_category = "blog"
                _add_pages(pages)

        # TripAdvisor
        if include_tripadvisor:
            _progress("discovering", "Searching TripAdvisor...")
            for query_template in TRIPADVISOR_QUERIES:
                query = query_template.format(city=city_query)
                pages = await self.search.search_ddg(query)
                _add_pages(pages)

        # --- Direct URL fallback ---
        # If search returned nothing (DDG blocked, etc.), generate pages
        # from known URL patterns for editorial + blog sources
        if not search_worked:
            _progress("discovering", "Search returned no results — using direct URL patterns...")
            logger.info("Search returned 0 pages, falling back to direct URL patterns for %s", city)
            all_sources = (
                (EDITORIAL_SOURCES if include_editorial else [])
                + (BLOG_SOURCES if include_blogs else [])
            )
            for source in all_sources:
                domain = source["domain"]
                patterns = DIRECT_URL_PATTERNS.get(domain, [])
                for pattern in patterns:
                    url = pattern.format(
                        city=city,
                        city_slug=city_slug,
                        country_slug=country_slug,
                    )
                    norm = url.rstrip("/").lower()
                    if norm not in seen_urls:
                        seen_urls.add(norm)
                        all_pages.append(DiscoveredPage(
                            url=url,
                            title="",
                            snippet="",
                            source_domain=domain,
                            source_category=source.get("category", "web"),
                            search_provider="direct_url",
                        ))

        return all_pages

    # -- Internal: fetch + extract ---

    async def _fetch_and_extract(self, page: DiscoveredPage) -> List[ExtractedPOI]:
        """Fetch a page and extract POIs from its text content."""
        await asyncio.sleep(self.rate_limit)
        try:
            resp = await self.search.client.get(page.url)
            if resp.status_code != 200:
                logger.info("HTTP %d fetching %s", resp.status_code, page.url[:80])
                return []
            text = extract_text_from_html(resp.text)
            if not text or len(text) < 50:
                return []
        except Exception as e:
            logger.warning("Error fetching %s: %s", page.url[:80], e)
            return []

        return self.extractor.extract_pois_from_text(
            text,
            source_url=page.url,
            source_domain=page.source_domain,
        )

    def _handle_tripadvisor(self, page: DiscoveredPage) -> List[ExtractedPOI]:
        """Extract POI from TripAdvisor search snippet (no page fetch)."""
        return self.extractor.extract_pois_from_snippet(
            title=page.title,
            snippet=page.snippet,
            source_url=page.url,
            source_domain=page.source_domain,
            rating=page.rating,
            review_count=page.review_count,
        )


def _dedup_pois(pois: List[ExtractedPOI]) -> List[ExtractedPOI]:
    """Deduplicate POIs by normalized name."""
    seen: set = set()
    unique: List[ExtractedPOI] = []
    for poi in pois:
        norm = _normalize_name(poi.name)
        if norm and norm not in seen:
            seen.add(norm)
            unique.append(poi)
    return unique
