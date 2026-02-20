"""
TripAdvisor Scraper for City Intelligence.
Discovers TripAdvisor pages via DuckDuckGo ``site:tripadvisor.com`` searches,
extracts ratings, review counts, and (for forum pages) richer text.

Reuses the same DuckDuckGo/HTML utilities from ``blog_scraper.py``.
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from urllib.parse import quote_plus

import httpx

from blog_scraper import (
    HEADERS,
    DDG_SEARCH_URL,
    DEFAULT_RATE_LIMIT,
    REQUEST_TIMEOUT,
    extract_text_from_html,
    parse_ddg_results,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Search categories — 2 queries each → 8 DDG requests per city
# ---------------------------------------------------------------------------

TRIPADVISOR_QUERIES: dict[str, list[str]] = {
    "things_to_do": [
        '"{city}" things to do',
        '"{city}" top attractions',
    ],
    "restaurants": [
        '"{city}" best restaurants',
        '"{city}" where to eat',
    ],
    "hidden_gems": [
        '"{city}" hidden gems',
        '"{city}" off the beaten path',
    ],
    "forums": [
        '"{city}" forum travel tips',
        '"{city}" forum itinerary advice',
    ],
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class TripAdvisorResult:
    """A single TripAdvisor page discovered via search."""
    title: str
    url: str
    snippet: str
    category: str  # things_to_do | restaurants | hidden_gems | forums
    rating: Optional[float] = None  # e.g. 4.5
    review_count: Optional[int] = None  # e.g. 1234
    enriched_text: str = ""  # richer body text from fetching the page

    def to_dict(self) -> dict:
        d: dict = {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet[:300] if self.snippet else "",
            "category": self.category,
        }
        if self.rating is not None:
            d["rating"] = self.rating
        if self.review_count is not None:
            d["review_count"] = self.review_count
        if self.enriched_text:
            d["enriched_text"] = self.enriched_text[:500]
        return d


@dataclass
class CityTripAdvisorData:
    """Container for all TripAdvisor data collected about a city."""
    city_name: str
    country: str = ""
    collected_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    results: list[TripAdvisorResult] = field(default_factory=list)

    def to_dict(self) -> dict:
        by_category: dict[str, list[dict]] = {}
        for r in self.results:
            by_category.setdefault(r.category, []).append(r.to_dict())
        return {
            "city_name": self.city_name,
            "country": self.country,
            "collected_at": self.collected_at,
            "total_results": len(self.results),
            "results_by_category": by_category,
            "results": [r.to_dict() for r in self.results],
        }


# ---------------------------------------------------------------------------
# Rating / review extraction from snippets
# ---------------------------------------------------------------------------

_RATING_RE = re.compile(
    r"(\d(?:\.\d)?)\s*(?:of|out of)\s*5"  # "4.5 of 5", "4 out of 5"
    r"|Rating:\s*(\d(?:\.\d)?)"            # "Rating: 4.5"
    r"|(\d(?:\.\d)?)\s*/\s*5",             # "4.5/5"
    re.IGNORECASE,
)

_REVIEW_COUNT_RE = re.compile(
    r"([\d,]+)\s*reviews?",
    re.IGNORECASE,
)


def _extract_rating(text: str) -> Optional[float]:
    m = _RATING_RE.search(text)
    if not m:
        return None
    raw = m.group(1) or m.group(2) or m.group(3)
    try:
        val = float(raw)
        return val if 0 <= val <= 5 else None
    except (ValueError, TypeError):
        return None


def _extract_review_count(text: str) -> Optional[int]:
    m = _REVIEW_COUNT_RE.search(text)
    if not m:
        return None
    try:
        return int(m.group(1).replace(",", ""))
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
# Scraper
# ---------------------------------------------------------------------------

class TripAdvisorScraper:
    """
    Discovers TripAdvisor pages for a city using DuckDuckGo
    ``site:tripadvisor.com`` searches.
    """

    def __init__(self, rate_limit_delay: float = DEFAULT_RATE_LIMIT) -> None:
        self.rate_limit_delay = rate_limit_delay
        self.client = httpx.AsyncClient(
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
            follow_redirects=True,
        )

    async def close(self) -> None:
        await self.client.aclose()

    async def _rate_limit(self) -> None:
        await asyncio.sleep(self.rate_limit_delay)

    async def _fetch_html(self, url: str) -> Optional[str]:
        await self._rate_limit()
        try:
            resp = await self.client.get(url)
            if resp.status_code == 200:
                return resp.text
            logger.info("HTTP %d for %s", resp.status_code, url[:120])
            return None
        except httpx.TimeoutException:
            logger.warning("Timeout fetching %s", url[:120])
            return None
        except Exception as e:
            logger.warning("Error fetching %s: %s", url[:120], e)
            return None

    # ------------------------------------------------------------------

    async def search_category(
        self,
        city: str,
        country: str,
        category: str,
        queries: list[str],
    ) -> list[TripAdvisorResult]:
        """Run DDG searches for one category and return parsed results."""
        results: list[TripAdvisorResult] = []
        seen_urls: set[str] = set()

        for template in queries:
            query_str = template.replace("{city}", city)
            full_query = f'site:tripadvisor.com {query_str}'
            if country:
                full_query += f' "{country}"'
            encoded = quote_plus(full_query)
            search_url = f"{DDG_SEARCH_URL}?q={encoded}"

            print(f"    DDG: {full_query}")
            html = await self._fetch_html(search_url)
            if not html:
                continue

            raw = parse_ddg_results(html)
            for r in raw:
                url = r.get("url", "")
                if "tripadvisor" not in url.lower():
                    continue
                norm = url.rstrip("/").lower()
                if norm in seen_urls:
                    continue
                seen_urls.add(norm)

                title = r.get("title", "").strip()
                snippet = r.get("snippet", "").strip()
                combined_text = f"{title} {snippet}"

                result = TripAdvisorResult(
                    title=title,
                    url=url,
                    snippet=snippet,
                    category=category,
                    rating=_extract_rating(combined_text),
                    review_count=_extract_review_count(combined_text),
                )
                results.append(result)

        return results

    async def _enrich_forum_results(self, results: list[TripAdvisorResult]) -> None:
        """Fetch actual TripAdvisor forum pages for richer text."""
        forum_results = [r for r in results if r.category == "forums"]
        for r in forum_results[:3]:  # limit to 3 page fetches
            html = await self._fetch_html(r.url)
            if html:
                body = extract_text_from_html(html)
                if body and len(body) > len(r.snippet):
                    r.enriched_text = body[:500]

    async def collect(self, city: str, country: str = "") -> CityTripAdvisorData:
        """Collect TripAdvisor data for a city."""
        print(f"\n{'='*60}")
        print(f"Collecting TripAdvisor data for: {city}, {country}")
        print(f"{'='*60}")

        data = CityTripAdvisorData(city_name=city, country=country)

        for category, queries in TRIPADVISOR_QUERIES.items():
            print(f"  Category: {category}")
            try:
                results = await self.search_category(city, country, category, queries)
                data.results.extend(results)
                print(f"    → {len(results)} result(s)")
            except Exception as e:
                logger.warning("TripAdvisor %s failed: %s", category, e)
                print(f"    → Error: {e}")

        # Enrich forum pages
        await self._enrich_forum_results(data.results)

        print(f"\n  Total TripAdvisor results: {len(data.results)}")
        return data


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def collect_tripadvisor_intelligence(
    city: str,
    country: str = "",
    output_file: Optional[str] = None,
) -> CityTripAdvisorData:
    """
    Main entry point — collect TripAdvisor data for a city.

    Args:
        city: City name (e.g. "Rome")
        country: Country for disambiguation (e.g. "Italy")
        output_file: Optional path to write JSON output.

    Returns:
        CityTripAdvisorData with all discovered results.
    """
    if not country:
        country = _guess_country(city)

    scraper = TripAdvisorScraper()
    try:
        data = await scraper.collect(city, country)

        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data.to_dict(), f, indent=2, ensure_ascii=False)
            print(f"\nSaved TripAdvisor data to {output_file}")

        return data
    finally:
        await scraper.close()


def _guess_country(city: str) -> str:
    """Auto-detect country from known city names."""
    city_country_map = {
        "rome": "Italy", "florence": "Italy", "venice": "Italy",
        "milan": "Italy", "naples": "Italy", "amalfi": "Italy",
        "paris": "France", "nice": "France", "lyon": "France",
        "bordeaux": "France",
        "barcelona": "Spain", "madrid": "Spain", "seville": "Spain",
        "granada": "Spain",
        "tokyo": "Japan", "kyoto": "Japan", "osaka": "Japan",
        "london": "UK", "edinburgh": "UK", "bath": "UK", "oxford": "UK",
        "berlin": "Germany", "munich": "Germany",
        "amsterdam": "Netherlands", "prague": "Czech Republic",
        "vienna": "Austria", "lisbon": "Portugal", "athens": "Greece",
        "bangkok": "Thailand", "delhi": "India", "mumbai": "India",
    }
    return city_country_map.get(city.lower(), "")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) < 2:
        print("Usage: python tripadvisor_scraper.py <city> [country] [output.json]")
        sys.exit(1)

    _city = sys.argv[1]
    _country = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].endswith(".json") else ""
    _output = sys.argv[-1] if sys.argv[-1].endswith(".json") else None

    asyncio.run(collect_tripadvisor_intelligence(_city, _country, _output))
