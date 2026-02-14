"""
City Intelligence Generator
Combines Reddit data, tour information, and blog resources
to generate comprehensive city intelligence reports.
"""
import asyncio
import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from pathlib import Path

from reddit_scraper import collect_city_intelligence, CityRedditData
from tours_events import collect_tours_events, CityToursEvents, WebSearchTours


@dataclass
class PersonaInsights:
    """Insights tailored for a specific traveler persona."""
    persona_name: str
    description: str
    recommended_posts: list = field(default_factory=list)
    recommended_tours: list = field(default_factory=list)
    key_tips: list = field(default_factory=list)
    things_to_avoid: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "persona_name": self.persona_name,
            "description": self.description,
            "recommended_posts": self.recommended_posts[:10],
            "recommended_tours": self.recommended_tours[:5],
            "key_tips": self.key_tips[:10],
            "things_to_avoid": self.things_to_avoid[:5],
        }


@dataclass
class CityIntelligenceReport:
    """Complete intelligence report for a city."""
    city_name: str
    generated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    summary: dict = field(default_factory=dict)
    reddit_data: dict = field(default_factory=dict)
    tours_events: dict = field(default_factory=dict)
    persona_insights: dict = field(default_factory=dict)
    blog_resources: dict = field(default_factory=dict)
    search_urls: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "city_name": self.city_name,
            "generated_at": self.generated_at,
            "summary": self.summary,
            "reddit_data": self.reddit_data,
            "tours_events": self.tours_events,
            "persona_insights": self.persona_insights,
            "blog_resources": self.blog_resources,
            "search_urls": self.search_urls,
        }


# Persona definitions
PERSONAS = {
    "solo_traveler": {
        "name": "Solo Traveler",
        "description": "Independent travelers exploring alone",
        "keywords": ["solo", "alone", "single", "backpacker", "hostel"],
        "interests": ["safety", "social", "meetup", "hostel", "budget"],
        "reddit_categories": ["general", "challenges", "budget", "neighborhoods"],
    },
    "couple": {
        "name": "Romantic Couple",
        "description": "Couples looking for romantic experiences",
        "keywords": ["couple", "romantic", "honeymoon", "anniversary", "date"],
        "interests": ["romantic", "scenic", "intimate", "dinner", "sunset"],
        "reddit_categories": ["general", "food", "neighborhoods"],
    },
    "family": {
        "name": "Family with Kids",
        "description": "Families traveling with children",
        "keywords": ["family", "kids", "children", "toddler", "stroller"],
        "interests": ["kid-friendly", "parks", "playground", "activities", "safe"],
        "reddit_categories": ["family", "general", "neighborhoods"],
    },
    "budget": {
        "name": "Budget Traveler",
        "description": "Cost-conscious travelers",
        "keywords": ["budget", "cheap", "free", "affordable", "backpacker"],
        "interests": ["free", "cheap eats", "hostel", "walking", "street food"],
        "reddit_categories": ["budget", "food", "general"],
    },
    "luxury": {
        "name": "Luxury Traveler",
        "description": "Travelers seeking premium experiences",
        "keywords": ["luxury", "upscale", "high-end", "boutique", "5-star"],
        "interests": ["fine dining", "spa", "exclusive", "premium", "luxury"],
        "reddit_categories": ["food", "neighborhoods", "general"],
    },
    "adventure": {
        "name": "Adventure Seeker",
        "description": "Active travelers seeking thrills",
        "keywords": ["adventure", "outdoor", "hiking", "extreme", "active"],
        "interests": ["hiking", "sports", "nature", "outdoor", "adrenaline"],
        "reddit_categories": ["general", "neighborhoods"],
    },
    "foodie": {
        "name": "Food Enthusiast",
        "description": "Travelers focused on culinary experiences",
        "keywords": ["food", "culinary", "restaurant", "eating", "cuisine"],
        "interests": ["restaurant", "street food", "market", "local cuisine", "cooking class"],
        "reddit_categories": ["food", "general", "neighborhoods"],
    },
    "culture": {
        "name": "Culture & History Buff",
        "description": "Travelers interested in history and culture",
        "keywords": ["culture", "history", "museum", "art", "heritage"],
        "interests": ["museum", "architecture", "historical", "tour", "heritage"],
        "reddit_categories": ["general", "neighborhoods"],
    },
}


# Blog resources by category
BLOG_RESOURCES = {
    "local_experience": [
        {"name": "Spotted by Locals", "url": "https://www.spottedbylocals.com/{city_slug}", "description": "Recommendations from locals only"},
        {"name": "Atlas Obscura", "url": "https://www.atlasobscura.com/things-to-do/{city_slug}", "description": "Hidden gems and unusual places"},
        {"name": "Culture Trip", "url": "https://theculturetrip.com/search?q={city}", "description": "Culture, food, and experiences"},
    ],
    "food": [
        {"name": "Eater", "url": "https://www.eater.com/{city_slug}", "description": "Restaurant guides and food news"},
        {"name": "TripAdvisor Restaurants", "url": "https://www.tripadvisor.com/Restaurants-{city}", "description": "Restaurant reviews"},
    ],
    "family": [
        {"name": "Mommy Poppins", "url": "https://mommypoppins.com/search?q={city}", "description": "Family activities"},
        {"name": "Trekaroo", "url": "https://www.trekaroo.com/search?utf8=%E2%9C%93&search%5Bq%5D={city}", "description": "Family travel reviews"},
    ],
    "budget": [
        {"name": "Nomadic Matt", "url": "https://www.nomadicmatt.com/?s={city}", "description": "Budget travel tips"},
        {"name": "Budget Your Trip", "url": "https://www.budgetyourtrip.com/search?q={city}", "description": "Cost breakdowns"},
    ],
    "general": [
        {"name": "Lonely Planet", "url": "https://www.lonelyplanet.com/search?q={city}", "description": "Comprehensive travel guides"},
        {"name": "Rick Steves", "url": "https://www.ricksteves.com/europe?searchTerm={city}", "description": "European travel expertise"},
        {"name": "Wikitravel", "url": "https://wikitravel.org/en/{city}", "description": "Community travel guide"},
    ],
}


class CityIntelligenceGenerator:
    """
    Generates comprehensive city intelligence reports by combining
    multiple data sources.
    """

    def __init__(self, output_dir: str = "city_intelligence/cities"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _generate_blog_resources(self, city: str) -> dict:
        """Generate blog resource URLs for the city."""
        city_slug = city.lower().replace(" ", "-")
        city_encoded = city.replace(" ", "+")

        resources = {}
        for category, blogs in BLOG_RESOURCES.items():
            resources[category] = []
            for blog in blogs:
                url = blog["url"].format(city=city_encoded, city_slug=city_slug)
                resources[category].append({
                    "name": blog["name"],
                    "url": url,
                    "description": blog["description"],
                })

        return resources

    def _extract_persona_insights(
        self,
        persona_id: str,
        reddit_data: CityRedditData,
        tours_data: CityToursEvents,
        city: str
    ) -> PersonaInsights:
        """Extract insights tailored to a specific persona."""
        persona = PERSONAS[persona_id]
        insights = PersonaInsights(
            persona_name=persona["name"],
            description=persona["description"],
        )

        # Extract relevant Reddit posts
        relevant_posts = []
        for category in persona["reddit_categories"]:
            if category in reddit_data.categories:
                for post in reddit_data.categories[category][:5]:
                    post_text = f"{post.title} {post.selftext}".lower()
                    relevance = sum(1 for kw in persona["keywords"] if kw in post_text)
                    if relevance > 0:
                        relevant_posts.append({
                            "title": post.title,
                            "url": f"https://reddit.com{post.permalink}",
                            "score": post.score,
                            "relevance": relevance,
                        })

        # Sort by relevance
        relevant_posts.sort(key=lambda x: (x["relevance"], x["score"]), reverse=True)
        insights.recommended_posts = relevant_posts[:10]

        # Extract tips from posts
        for post in reddit_data.posts[:50]:
            post_text = f"{post.title} {post.selftext}".lower()
            for interest in persona["interests"]:
                if interest in post_text and len(post.title) < 200:
                    insights.key_tips.append(post.title)
                    break

        # Extract things to avoid
        for post in reddit_data.categories.get("challenges", [])[:10]:
            insights.things_to_avoid.append(post.title)

        # Match tours
        if persona_id == "foodie":
            insights.recommended_tours = [t.to_dict() for t in tours_data.food_tours[:5]]
        elif persona_id == "culture":
            insights.recommended_tours = [t.to_dict() for t in tours_data.history_tours[:5]]
        elif persona_id == "budget":
            insights.recommended_tours = [t.to_dict() for t in tours_data.free_tours[:5]]
        else:
            insights.recommended_tours = [t.to_dict() for t in tours_data.walking_tours[:5]]

        return insights

    def _generate_summary(
        self,
        reddit_data: CityRedditData,
        tours_data: CityToursEvents,
        city: str
    ) -> dict:
        """Generate a summary of city intelligence."""
        # Extract top highlights from Reddit
        top_posts = sorted(reddit_data.posts, key=lambda x: x.score, reverse=True)[:5]
        highlights = [p.title for p in top_posts]

        # Count categories
        category_counts = {cat: len(posts) for cat, posts in reddit_data.categories.items()}

        return {
            "city_name": city,
            "data_sources": {
                "reddit_posts": len(reddit_data.posts),
                "subreddits": reddit_data.subreddits_found,
                "walking_tours": len(tours_data.walking_tours),
                "food_tours": len(tours_data.food_tours),
                "free_tours": len(tours_data.free_tours),
                "events": len(tours_data.events),
            },
            "category_breakdown": category_counts,
            "top_highlights": highlights,
            "has_family_content": len(reddit_data.categories.get("family", [])) > 0,
            "has_food_content": len(reddit_data.categories.get("food", [])) > 0,
            "has_budget_content": len(reddit_data.categories.get("budget", [])) > 0,
        }

    async def generate_report(
        self,
        city: str,
        viator_key: str = "",
        gyg_key: str = "",
        eventbrite_token: str = "",
        save_to_file: bool = True
    ) -> CityIntelligenceReport:
        """
        Generate a complete city intelligence report.

        Args:
            city: Name of the city
            viator_key: Viator API key (optional)
            gyg_key: GetYourGuide API key (optional)
            eventbrite_token: Eventbrite token (optional)
            save_to_file: Whether to save the report to a JSON file

        Returns:
            CityIntelligenceReport object
        """
        print(f"\n{'='*60}")
        print(f"GENERATING CITY INTELLIGENCE REPORT: {city}")
        print(f"{'='*60}")

        report = CityIntelligenceReport(city_name=city)

        # Collect Reddit data
        print("\n[1/4] Collecting Reddit data...")
        reddit_data = await collect_city_intelligence(city)
        report.reddit_data = reddit_data.to_dict()

        # Collect tours and events
        print("\n[2/4] Collecting tours and events...")
        tours_data = await collect_tours_events(
            city,
            viator_key=viator_key,
            gyg_key=gyg_key,
            eventbrite_token=eventbrite_token
        )
        report.tours_events = tours_data.to_dict()

        # Generate persona insights
        print("\n[3/4] Generating persona insights...")
        for persona_id in PERSONAS:
            insights = self._extract_persona_insights(
                persona_id, reddit_data, tours_data, city
            )
            report.persona_insights[persona_id] = insights.to_dict()
            print(f"  - {PERSONAS[persona_id]['name']}: {len(insights.recommended_posts)} posts, {len(insights.key_tips)} tips")

        # Generate blog resources
        print("\n[4/4] Generating blog resources...")
        report.blog_resources = self._generate_blog_resources(city)

        # Generate search URLs
        report.search_urls = WebSearchTours.get_search_urls(city)

        # Generate summary
        report.summary = self._generate_summary(reddit_data, tours_data, city)

        # Save to file
        if save_to_file:
            city_slug = city.lower().replace(" ", "_")
            output_path = self.output_dir / f"{city_slug}_intelligence.json"
            with open(output_path, 'w') as f:
                json.dump(report.to_dict(), f, indent=2)
            print(f"\n✓ Report saved to: {output_path}")

            # Also generate a markdown summary
            md_path = self.output_dir / f"{city_slug}_summary.md"
            self._generate_markdown_summary(report, md_path)
            print(f"✓ Summary saved to: {md_path}")

        print(f"\n{'='*60}")
        print(f"REPORT COMPLETE: {city}")
        print(f"  Reddit posts: {len(reddit_data.posts)}")
        print(f"  Tours found: {len(tours_data.walking_tours) + len(tours_data.food_tours)}")
        print(f"  Personas analyzed: {len(PERSONAS)}")
        print(f"{'='*60}")

        return report

    def _generate_markdown_summary(self, report: CityIntelligenceReport, output_path: Path):
        """Generate a human-readable markdown summary."""
        city = report.city_name
        summary = report.summary

        md_content = f"""# {city} - City Intelligence Report

Generated: {report.generated_at}

## Overview

| Metric | Value |
|--------|-------|
| Reddit Posts Collected | {summary['data_sources']['reddit_posts']} |
| Subreddits Found | {', '.join(summary['data_sources']['subreddits']) or 'None'} |
| Walking Tours | {summary['data_sources']['walking_tours']} |
| Food Tours | {summary['data_sources']['food_tours']} |
| Free Tours | {summary['data_sources']['free_tours']} |
| Events | {summary['data_sources']['events']} |

## Top Highlights (from Reddit)

{chr(10).join(f'- {h}' for h in summary['top_highlights'][:5])}

## Category Breakdown

"""
        for cat, count in summary.get('category_breakdown', {}).items():
            md_content += f"- **{cat.replace('_', ' ').title()}**: {count} posts\n"

        md_content += "\n## Persona Recommendations\n\n"

        for persona_id, insights in report.persona_insights.items():
            md_content += f"""### {insights['persona_name']}
{insights['description']}

**Key Tips:**
{chr(10).join(f'- {tip}' for tip in insights['key_tips'][:3]) or '- No specific tips found'}

**Things to Avoid:**
{chr(10).join(f'- {avoid}' for avoid in insights['things_to_avoid'][:3]) or '- No warnings found'}

---

"""

        md_content += """## Useful Links

### Tour Platforms
"""
        for platform, url in report.search_urls.items():
            md_content += f"- [{platform.replace('_', ' ').title()}]({url})\n"

        md_content += "\n### Blog Resources\n"
        for category, blogs in report.blog_resources.items():
            md_content += f"\n**{category.replace('_', ' ').title()}:**\n"
            for blog in blogs:
                md_content += f"- [{blog['name']}]({blog['url']}) - {blog['description']}\n"

        with open(output_path, 'w') as f:
            f.write(md_content)


async def generate_city_report(
    city: str,
    output_dir: str = "city_intelligence/cities",
    viator_key: str = "",
    gyg_key: str = "",
    eventbrite_token: str = ""
) -> CityIntelligenceReport:
    """
    Main function to generate a city intelligence report.

    This is the entry point for the city intelligence system.
    Call this function whenever a new city is added to generate
    comprehensive travel intelligence.

    Args:
        city: Name of the city (e.g., "Toronto", "New York", "Paris")
        output_dir: Directory to save output files
        viator_key: Viator API key (optional)
        gyg_key: GetYourGuide API key (optional)
        eventbrite_token: Eventbrite token (optional)

    Returns:
        CityIntelligenceReport object containing all collected data
    """
    generator = CityIntelligenceGenerator(output_dir)
    return await generator.generate_report(
        city,
        viator_key=viator_key,
        gyg_key=gyg_key,
        eventbrite_token=eventbrite_token
    )


# CLI usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m city_intelligence.generator <city_name>")
        print("Example: python -m city_intelligence.generator Toronto")
        sys.exit(1)

    city = sys.argv[1]

    # Load API keys from environment
    viator_key = os.getenv("VIATOR_API_KEY", "")
    gyg_key = os.getenv("GYG_API_KEY", "")
    eventbrite_token = os.getenv("EVENTBRITE_TOKEN", "")

    asyncio.run(generate_city_report(city, viator_key=viator_key, gyg_key=gyg_key, eventbrite_token=eventbrite_token))
