"""
City Intelligence System
========================

Automatically generates comprehensive travel intelligence for cities by:
- Scraping Reddit for local insights, reviews, and recommendations
- Collecting walking tours and events from various platforms
- Generating persona-specific recommendations
- Compiling blog and resource links

Usage:
------

# Generate report for a city
from city_intelligence import generate_city_report
import asyncio

report = asyncio.run(generate_city_report("Toronto"))

# Or use the CLI
python -m city_intelligence.generator Toronto

Output:
-------
- JSON file with all collected data
- Markdown summary for human reading
- Persona-specific recommendations
- Links to tour platforms and blogs

API Integration:
----------------
Call generate_city_report() when adding a new city to EDT.
This will automatically create the intelligence files.
"""

from .generator import generate_city_report, CityIntelligenceReport, CityIntelligenceGenerator
from .reddit_scraper import collect_city_intelligence, RedditScraper
from .tours_events import collect_tours_events, WebSearchTours

__all__ = [
    "generate_city_report",
    "CityIntelligenceReport",
    "CityIntelligenceGenerator",
    "collect_city_intelligence",
    "RedditScraper",
    "collect_tours_events",
    "WebSearchTours",
]

__version__ = "1.0.0"
