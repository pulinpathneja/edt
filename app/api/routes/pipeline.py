import asyncio
import json
import logging
import os
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import BaseModel
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

from app.api.deps import get_db
from app.core.country_config import CITY_BBOXES
from app.core.database import AsyncSessionLocal
from app.core.embeddings import generate_embedding
from app.models.poi import POI
from app.models.city_insight import CityInsight
from app.services.data_ingestion.overture_fetcher import DatabaseSeeder, OvertureMapsFetcher
from app.services.data_ingestion.sample_data_converter import convert_sample_activities
from app.services.data_ingestion.crawl_to_poi_converter import (
    convert_blog_insights,
    convert_tripadvisor_insights,
)
from app.services.data_ingestion.web_poi_crawler import WebPOICrawler
from app.services.data_ingestion.auto_crawl_converter import convert_extracted_pois

# Add city_intelligence to path for imports
_ci_dir = str(Path(__file__).resolve().parents[3] / "city_intelligence")
if _ci_dir not in sys.path:
    sys.path.insert(0, _ci_dir)

router = APIRouter()

# In-memory task tracking
_crawl_tasks: Dict[str, dict] = {}
_intel_tasks: Dict[str, dict] = {}
_seed_tasks: Dict[str, dict] = {}
_crawl_poi_tasks: Dict[str, dict] = {}
_auto_crawl_tasks: Dict[str, dict] = {}
_url_crawl_tasks: Dict[str, dict] = {}

# City Intelligence output dir
INTEL_OUTPUT_DIR = Path(os.getenv("CITY_INTEL_OUTPUT_DIR", "city_intelligence/cities"))
INTEL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# --- Request/Response Models ---

class CrawlRequest(BaseModel):
    city: str
    limit: int = 500


class IntelCrawlRequest(BaseModel):
    city: str
    country: str = ""
    force_refresh: bool = False


class SearchRequest(BaseModel):
    query: str
    city: Optional[str] = None
    category: Optional[str] = None
    limit: int = 10


class SeedDbRequest(BaseModel):
    city: Optional[str] = None
    include_seed_json: bool = True
    include_sample_data: bool = True


class CrawlPoisRequest(BaseModel):
    city: str
    country: Optional[str] = None
    include_blogs: bool = True
    include_tripadvisor: bool = True


class AutoCrawlRequest(BaseModel):
    city: str
    country: str = ""
    include_open_web: bool = True
    include_editorial: bool = True
    include_blogs: bool = True
    include_tripadvisor: bool = True


class UrlCrawlRequest(BaseModel):
    urls: List[str]
    city: str
    country: str = ""


# --- Background Tasks ---

async def _run_crawl(task_id: str, city: str, limit: int):
    """Background task: Overture Maps POI crawl pipeline."""
    task = _crawl_tasks[task_id]
    task["status"] = "running"
    task["message"] = f"Fetching POIs from Overture Maps for {city}..."
    start = time.time()

    try:
        fetcher = OvertureMapsFetcher()
        raw_pois = await asyncio.to_thread(fetcher.fetch_pois, city, limit)
        task["pois_fetched"] = len(raw_pois)
        task["message"] = f"Scoring {len(raw_pois)} POIs..."

        scored_pois = await asyncio.to_thread(fetcher.score_pois, raw_pois, city)
        task["message"] = f"Embedding & inserting {len(scored_pois)} POIs into database..."

        async with AsyncSessionLocal() as session:
            seeder = DatabaseSeeder(session)
            inserted = await seeder.seed_pois(scored_pois, city)
            await session.commit()
            task["pois_inserted"] = inserted

        await asyncio.to_thread(DatabaseSeeder.save_seed_json, scored_pois, city)

        task["status"] = "completed"
        task["message"] = f"Successfully crawled {city}: {inserted} POIs inserted"
        task["duration_seconds"] = round(time.time() - start, 1)

    except Exception as e:
        task["status"] = "failed"
        task["error"] = str(e)
        task["message"] = f"Crawl failed: {str(e)}"
        task["duration_seconds"] = round(time.time() - start, 1)


def _compute_persona_tags(post) -> list[str]:
    """Auto-tag a Reddit post with matching persona IDs."""
    from generator import PERSONAS
    text = f"{post.title} {post.selftext}".lower()
    tags = []
    for pid, persona in PERSONAS.items():
        if any(kw in text for kw in persona["keywords"]):
            tags.append(pid)
    return tags


async def _store_insights_to_db(
    city: str,
    country: str,
    reddit_data,
    blog_data,
    tripadvisor_data,
) -> int:
    """
    Persist scraped intelligence to the ``city_insights`` table.
    Clears old rows for the city first, then bulk-inserts new ones.
    Returns the number of rows inserted.
    """
    rows: list[CityInsight] = []
    city_lower = city.lower()

    # --- Reddit posts ---
    if reddit_data:
        for post in reddit_data.posts:
            rows.append(CityInsight(
                city=city_lower,
                country=country,
                source="reddit",
                category=post.category or "general",
                title=post.title,
                content=(post.selftext or "")[:2000],
                url=f"https://reddit.com{post.permalink}" if post.permalink else "",
                relevance_score=post.relevance_score,
                author=f"r/{post.subreddit}",
                source_date=datetime.utcfromtimestamp(post.created_utc) if post.created_utc else None,
                metadata_={
                    "score": post.score,
                    "num_comments": post.num_comments,
                    "subreddit": post.subreddit,
                },
                persona_tags=_compute_persona_tags(post),
            ))

    # --- Blog articles ---
    if blog_data:
        for article in blog_data.articles:
            rows.append(CityInsight(
                city=city_lower,
                country=country,
                source="blog",
                category=article.category or "general",
                title=article.title,
                content=(article.snippet or "")[:2000],
                url=article.url,
                relevance_score=0.0,
                author=article.source,
                metadata_={"blog_source": article.source},
            ))

    # --- TripAdvisor results ---
    if tripadvisor_data:
        for result in tripadvisor_data.results:
            rows.append(CityInsight(
                city=city_lower,
                country=country,
                source="tripadvisor",
                category=result.category or "general",
                title=result.title,
                content=(result.snippet or "")[:2000],
                url=result.url,
                relevance_score=0.0,
                rating=result.rating,
                metadata_={
                    "review_count": result.review_count,
                    "enriched_text": (result.enriched_text or "")[:500],
                },
            ))

    if not rows:
        return 0

    async with AsyncSessionLocal() as session:
        # Clear previous data for this city
        from sqlalchemy import delete
        await session.execute(
            delete(CityInsight).where(CityInsight.city == city_lower)
        )
        session.add_all(rows)
        await session.commit()

    return len(rows)


async def _run_intel_crawl(task_id: str, city: str, country: str = ""):
    """Background task: City Intelligence crawl (Reddit + blogs + TripAdvisor + tours + report)."""
    task = _intel_tasks[task_id]
    task["status"] = "running"
    task["stage"] = "Importing modules..."
    start = time.time()

    try:
        from reddit_scraper import collect_city_intelligence
        from blog_scraper import collect_blog_intelligence
        from tripadvisor_scraper import collect_tripadvisor_intelligence
        from tours_events import collect_tours_events
        from generator import CityIntelligenceGenerator

        # Stage 1: Reddit
        task["stage"] = "Crawling Reddit..."
        task["message"] = f"Crawling Reddit for {city} ({country}) travel insights..."
        reddit_data = await collect_city_intelligence(city, country=country)
        reddit_posts = len(reddit_data.posts)
        task["reddit_posts"] = reddit_posts
        task["message"] = f"Found {reddit_posts} Reddit posts. Crawling travel blogs..."

        # Stage 2: Travel Blogs
        task["stage"] = "Crawling blogs..."
        task["message"] = f"Crawling travel blogs for {city} ({country})..."
        blog_data = None
        blog_articles = 0
        try:
            blog_data = await collect_blog_intelligence(city, country=country)
            blog_articles = len(blog_data.articles)
            task["blog_articles"] = blog_articles
            task["message"] = f"Found {blog_articles} blog articles. Crawling TripAdvisor..."
        except Exception as blog_err:
            logger.warning(f"Blog scraping failed (non-fatal): {blog_err}")
            task["blog_articles"] = 0
            task["message"] = "Blog scraping skipped. Crawling TripAdvisor..."

        # Stage 3: TripAdvisor (non-fatal)
        task["stage"] = "Crawling TripAdvisor..."
        task["message"] = f"Crawling TripAdvisor for {city}..."
        tripadvisor_data = None
        ta_count = 0
        try:
            tripadvisor_data = await collect_tripadvisor_intelligence(city, country=country)
            ta_count = len(tripadvisor_data.results)
            task["tripadvisor_results"] = ta_count
            task["message"] = f"Found {ta_count} TripAdvisor results. Fetching tours..."
        except Exception as ta_err:
            logger.warning(f"TripAdvisor scraping failed (non-fatal): {ta_err}")
            task["tripadvisor_results"] = 0
            task["message"] = "TripAdvisor scraping skipped. Fetching tours..."

        # Stage 4: Tours & Events
        task["stage"] = "Fetching tours..."
        task["message"] = f"Fetching walking tours & events for {city}..."
        tours_data = await collect_tours_events(city)
        tours_count = len(tours_data.walking_tours) + len(tours_data.food_tours)
        task["tours_found"] = tours_count
        task["message"] = f"Found {tours_count} tours. Generating report..."

        # Stage 5: Generate report — pass pre-fetched data to avoid double scraping
        task["stage"] = "Generating report..."
        task["message"] = f"Generating intelligence report for {city}..."
        generator = CityIntelligenceGenerator(str(INTEL_OUTPUT_DIR))
        report = await generator.generate_report(
            city,
            country=country,
            save_to_file=True,
            reddit_data=reddit_data,
            tours_data=tours_data,
            blog_data=blog_data,
        )

        # Save blog data alongside the report
        if blog_data:
            blog_output = INTEL_OUTPUT_DIR / f"{city.lower().replace(' ', '_')}_blogs.json"
            with open(blog_output, 'w') as f:
                json.dump(blog_data.to_dict(), f, indent=2)

        # Save TripAdvisor data alongside the report
        if tripadvisor_data:
            ta_output = INTEL_OUTPUT_DIR / f"{city.lower().replace(' ', '_')}_tripadvisor.json"
            with open(ta_output, 'w') as f:
                json.dump(tripadvisor_data.to_dict(), f, indent=2)

        # Stage 6: Store to database (non-fatal — JSON is always written)
        task["stage"] = "Storing to database..."
        task["message"] = f"Persisting insights to database for {city}..."
        db_rows = 0
        try:
            db_rows = await _store_insights_to_db(
                city, country, reddit_data, blog_data, tripadvisor_data
            )
            task["db_rows"] = db_rows
        except Exception as db_err:
            logger.warning(f"DB storage failed (non-fatal): {db_err}")
            task["db_rows"] = 0
            task["db_error"] = str(db_err)

        task["status"] = "completed"
        task["stage"] = "Done"
        task["message"] = (
            f"Intelligence report ready for {city}: "
            f"{reddit_posts} Reddit posts, {blog_articles} blog articles, "
            f"{ta_count} TripAdvisor results, {tours_count} tours, "
            f"{db_rows} DB rows"
        )
        task["duration_seconds"] = round(time.time() - start, 1)

    except Exception as e:
        task["status"] = "failed"
        task["error"] = str(e)
        task["stage"] = "Failed"
        task["message"] = f"Crawl failed: {str(e)}"
        task["duration_seconds"] = round(time.time() - start, 1)


async def _run_seed_db(task_id: str, city: Optional[str], include_seed_json: bool, include_sample_data: bool):
    """Background task: Seed the vector DB from seed JSONs and/or sample itinerary data."""
    task = _seed_tasks[task_id]
    task["status"] = "running"
    task["message"] = "Starting database seed..."
    start = time.time()

    total_inserted = 0

    try:
        # Import seed_data functions
        seed_data_dir = Path(__file__).resolve().parents[3] / "data" / "scripts"
        if str(seed_data_dir.parent.parent) not in sys.path:
            sys.path.insert(0, str(seed_data_dir.parent.parent))
        from data.scripts.seed_data import seed_pois, get_seed_files, load_seed_data

        # Path 1: Load seed JSONs (Rome, Paris, etc.)
        if include_seed_json:
            task["message"] = "Loading seed JSON files..."
            seed_files = get_seed_files(city)
            task["seed_files_found"] = len(seed_files)

            for seed_file in seed_files:
                file_city = seed_file.stem.replace("_pois", "").title()
                task["message"] = f"Inserting seed data for {file_city}..."
                data = await load_seed_data(seed_file)
                pois_list = data.get("pois", [])

                async with AsyncSessionLocal() as session:
                    count = await seed_pois(session, pois_list, data.get("city", file_city))
                    total_inserted += count
                    task["pois_from_seed_json"] = task.get("pois_from_seed_json", 0) + count

        # Path 2: Convert sample itinerary data
        if include_sample_data:
            task["message"] = "Converting sample itinerary data..."
            sample_pois = convert_sample_activities(city)
            task["sample_pois_converted"] = len(sample_pois)

            if sample_pois:
                task["message"] = f"Inserting {len(sample_pois)} sample POIs..."
                async with AsyncSessionLocal() as session:
                    count = await seed_pois(session, sample_pois, city or "multi")
                    total_inserted += count
                    task["pois_from_sample"] = count

        task["status"] = "completed"
        task["total_inserted"] = total_inserted
        task["message"] = f"Seed complete: {total_inserted} POIs inserted"
        task["duration_seconds"] = round(time.time() - start, 1)

    except Exception as e:
        logger.exception(f"Seed DB failed: {e}")
        task["status"] = "failed"
        task["error"] = str(e)
        task["message"] = f"Seed failed: {str(e)}"
        task["total_inserted"] = total_inserted
        task["duration_seconds"] = round(time.time() - start, 1)


async def _run_crawl_pois(task_id: str, city: str, country: str, include_blogs: bool, include_tripadvisor: bool):
    """Background task: Extract POIs from city_insights table or run crawlers directly."""
    task = _crawl_poi_tasks[task_id]
    task["status"] = "running"
    task["message"] = f"Extracting POIs for {city}..."
    start = time.time()

    total_inserted = 0
    city_key = city.lower().replace(" ", "_")

    try:
        from data.scripts.seed_data import seed_pois

        # Check for existing insights in the database
        blog_insights = []
        ta_insights = []

        async with AsyncSessionLocal() as session:
            if include_blogs:
                task["message"] = f"Querying blog insights for {city}..."
                stmt = select(CityInsight).where(
                    CityInsight.city == city_key,
                    CityInsight.source == "blog",
                )
                result = await session.execute(stmt)
                blog_insights = result.scalars().all()
                task["blog_insights_found"] = len(blog_insights)

            if include_tripadvisor:
                task["message"] = f"Querying TripAdvisor insights for {city}..."
                stmt = select(CityInsight).where(
                    CityInsight.city == city_key,
                    CityInsight.source == "tripadvisor",
                )
                result = await session.execute(stmt)
                ta_insights = result.scalars().all()
                task["tripadvisor_insights_found"] = len(ta_insights)

        # If no insights found, try running crawlers directly
        if not blog_insights and not ta_insights:
            task["message"] = f"No insights in DB. Running crawlers for {city}..."
            try:
                if include_blogs:
                    task["message"] = f"Crawling blogs for {city}..."
                    from blog_scraper import collect_blog_intelligence
                    blog_data = await collect_blog_intelligence(city, country=country)
                    if blog_data and blog_data.articles:
                        # Convert articles to insight-like dicts
                        blog_insights = [
                            {
                                "title": a.title,
                                "content": a.snippet or "",
                                "category": a.category or "general",
                                "author": a.source or "",
                            }
                            for a in blog_data.articles
                        ]
                        task["blog_insights_found"] = len(blog_insights)

                if include_tripadvisor:
                    task["message"] = f"Crawling TripAdvisor for {city}..."
                    from tripadvisor_scraper import collect_tripadvisor_intelligence
                    ta_data = await collect_tripadvisor_intelligence(city, country=country)
                    if ta_data and ta_data.results:
                        ta_insights = [
                            {
                                "title": r.title,
                                "content": r.snippet or "",
                                "category": r.category or "general",
                                "rating": r.rating,
                                "metadata": {"review_count": r.review_count},
                            }
                            for r in ta_data.results
                        ]
                        task["tripadvisor_insights_found"] = len(ta_insights)
            except Exception as crawl_err:
                logger.warning(f"Direct crawl failed (non-fatal): {crawl_err}")
                task["crawl_error"] = str(crawl_err)

        # Convert blog insights to POIs
        if blog_insights:
            task["message"] = f"Converting {len(blog_insights)} blog insights to POIs..."
            blog_pois = convert_blog_insights(blog_insights, city_key)
            task["blog_pois_converted"] = len(blog_pois)

            if blog_pois:
                async with AsyncSessionLocal() as session:
                    count = await seed_pois(session, blog_pois, city.title())
                    total_inserted += count
                    task["blog_pois_inserted"] = count

        # Convert TripAdvisor insights to POIs
        if ta_insights:
            task["message"] = f"Converting {len(ta_insights)} TripAdvisor insights to POIs..."
            ta_pois = convert_tripadvisor_insights(ta_insights, city_key)
            task["tripadvisor_pois_converted"] = len(ta_pois)

            if ta_pois:
                async with AsyncSessionLocal() as session:
                    count = await seed_pois(session, ta_pois, city.title())
                    total_inserted += count
                    task["tripadvisor_pois_inserted"] = count

        task["status"] = "completed"
        task["total_inserted"] = total_inserted
        task["message"] = f"POI extraction complete for {city}: {total_inserted} POIs inserted"
        task["duration_seconds"] = round(time.time() - start, 1)

    except Exception as e:
        logger.exception(f"Crawl POIs failed: {e}")
        task["status"] = "failed"
        task["error"] = str(e)
        task["message"] = f"POI extraction failed: {str(e)}"
        task["total_inserted"] = total_inserted
        task["duration_seconds"] = round(time.time() - start, 1)


# --- Endpoints ---

@router.get("/cities")
async def list_cities():
    """List all available cities from CITY_BBOXES."""
    cities = [
        {"key": key, "country": bbox["country"]}
        for key, bbox in CITY_BBOXES.items()
    ]
    return cities


@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Get POI counts per city from the database."""
    try:
        stmt = select(POI.city, func.count(POI.id)).group_by(POI.city)
        result = await db.execute(stmt)
        rows = result.all()

        cities = [{"city": city, "count": count} for city, count in rows if city]
        total = sum(c["count"] for c in cities)

        return {"cities": cities, "total": total}
    except Exception as e:
        logger.warning(f"Failed to fetch stats: {e}")
        return {"cities": [], "total": 0, "error": "Database unavailable"}


# --- Overture Maps Crawl ---

@router.post("/crawl")
async def start_crawl(request: CrawlRequest, background_tasks: BackgroundTasks):
    """Trigger Overture Maps POI crawl for a city."""
    city = request.city.lower()
    if city not in CITY_BBOXES:
        return {"error": f"Unknown city: {city}. Use GET /pipeline/cities for available cities."}

    task_id = str(uuid.uuid4())
    _crawl_tasks[task_id] = {
        "task_id": task_id,
        "city": city,
        "status": "started",
        "message": "Crawl queued...",
        "pois_fetched": 0,
        "pois_inserted": 0,
        "duration_seconds": None,
        "error": None,
    }

    background_tasks.add_task(_run_crawl, task_id, city, request.limit)

    return {"task_id": task_id, "status": "started"}


@router.get("/crawl/{task_id}")
async def get_crawl_status(task_id: str):
    """Poll the status of an Overture Maps crawl task."""
    task = _crawl_tasks.get(task_id)
    if not task:
        return {"error": "Task not found"}
    return task


# --- City Intelligence Crawl (Reddit + Tours + Blogs) ---

@router.post("/intel/crawl")
async def start_intel_crawl(request: IntelCrawlRequest, background_tasks: BackgroundTasks):
    """Trigger City Intelligence crawl (Reddit + tours + blog resources)."""
    city = request.city.strip()
    if not city:
        return {"error": "City name is required"}

    city_slug = city.lower().replace(" ", "_")

    # Check if report already exists
    json_path = INTEL_OUTPUT_DIR / f"{city_slug}_intelligence.json"
    if json_path.exists() and not request.force_refresh:
        return {
            "status": "exists",
            "city": city,
            "message": f"Intelligence report already exists for {city}. Use force_refresh to regenerate.",
        }

    task_id = str(uuid.uuid4())
    _intel_tasks[task_id] = {
        "task_id": task_id,
        "city": city,
        "status": "started",
        "stage": "Queued",
        "message": "Intelligence crawl queued...",
        "reddit_posts": 0,
        "tours_found": 0,
        "duration_seconds": None,
        "error": None,
    }

    country = request.country.strip()
    # Auto-detect country from known cities if not provided
    if not country:
        from app.core.country_config import CITY_BBOXES
        city_key = city.lower().replace(" ", "_")
        if city_key in CITY_BBOXES:
            country = CITY_BBOXES[city_key].get("country", "")

    background_tasks.add_task(_run_intel_crawl, task_id, city, country)

    return {"task_id": task_id, "status": "started", "city": city, "country": country}


@router.get("/intel/crawl/{task_id}")
async def get_intel_crawl_status(task_id: str):
    """Poll the status of a City Intelligence crawl task."""
    task = _intel_tasks.get(task_id)
    if not task:
        return {"error": "Task not found"}
    return task


@router.get("/intel/cities")
async def list_intel_cities():
    """List all cities with completed intelligence reports."""
    cities = []
    for file in INTEL_OUTPUT_DIR.glob("*_intelligence.json"):
        city_slug = file.stem.replace("_intelligence", "")
        city_name = city_slug.replace("_", " ").title()
        try:
            with open(file) as f:
                data = json.load(f)
            cities.append({
                "city": city_name,
                "slug": city_slug,
                "generated_at": data.get("generated_at"),
                "reddit_posts": data.get("summary", {}).get("data_sources", {}).get("reddit_posts", 0),
            })
        except Exception:
            cities.append({"city": city_name, "slug": city_slug})

    return {"cities": cities, "total": len(cities)}


@router.get("/intel/report/{city_slug}")
async def get_intel_report(city_slug: str):
    """Get the full intelligence report for a city."""
    city = city_slug.replace("_", " ").title()
    json_path = INTEL_OUTPUT_DIR / f"{city_slug}_intelligence.json"

    if not json_path.exists():
        return {"error": f"No report found for {city}. Run a crawl first."}

    with open(json_path) as f:
        return json.load(f)


@router.get("/intel/summary/{city_slug}")
async def get_intel_summary(city_slug: str):
    """Get a simplified summary of a city intelligence report."""
    city = city_slug.replace("_", " ").title()
    json_path = INTEL_OUTPUT_DIR / f"{city_slug}_intelligence.json"

    if not json_path.exists():
        return {"error": f"No report found for {city}."}

    with open(json_path) as f:
        data = json.load(f)

    return {
        "city": data.get("city_name", city),
        "generated_at": data.get("generated_at"),
        "summary": data.get("summary", {}),
        "personas": list(data.get("persona_insights", {}).keys()),
        "search_urls": data.get("search_urls", {}),
    }


# --- City Insights from DB ---

@router.get("/intel/insights/{city_slug}")
async def get_city_insights(
    city_slug: str,
    source: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """Query stored city insights from the database with optional filters."""
    city = city_slug.lower().replace("-", "_").replace(" ", "_")

    try:
        stmt = select(CityInsight).where(CityInsight.city == city)

        if source:
            stmt = stmt.where(CityInsight.source == source.lower())
        if category:
            stmt = stmt.where(CityInsight.category == category.lower())

        stmt = stmt.order_by(CityInsight.relevance_score.desc()).limit(limit)

        result = await db.execute(stmt)
        rows = result.scalars().all()

        insights = []
        for row in rows:
            insights.append({
                "id": str(row.id),
                "city": row.city,
                "country": row.country,
                "source": row.source,
                "category": row.category,
                "title": row.title,
                "content": row.content[:500] if row.content else "",
                "url": row.url,
                "relevance_score": row.relevance_score,
                "rating": row.rating,
                "author": row.author,
                "persona_tags": row.persona_tags or [],
                "created_at": row.created_at.isoformat() if row.created_at else None,
            })

        return {"city": city, "total": len(insights), "insights": insights}
    except Exception as e:
        logger.warning(f"Insights query failed: {e}")
        return {"city": city, "total": 0, "insights": [], "error": str(e)}


# --- Seed Database ---

@router.post("/seed-db")
async def start_seed_db(request: SeedDbRequest, background_tasks: BackgroundTasks):
    """Seed the vector database from seed JSONs and/or sample itinerary data."""
    if not request.include_seed_json and not request.include_sample_data:
        return {"error": "At least one of include_seed_json or include_sample_data must be true."}

    task_id = str(uuid.uuid4())
    _seed_tasks[task_id] = {
        "task_id": task_id,
        "city": request.city,
        "status": "started",
        "message": "Seed task queued...",
        "total_inserted": 0,
        "pois_from_seed_json": 0,
        "pois_from_sample": 0,
        "seed_files_found": 0,
        "sample_pois_converted": 0,
        "duration_seconds": None,
        "error": None,
    }

    background_tasks.add_task(
        _run_seed_db, task_id, request.city,
        request.include_seed_json, request.include_sample_data,
    )

    return {"task_id": task_id, "status": "started"}


@router.get("/seed-db/{task_id}")
async def get_seed_db_status(task_id: str):
    """Poll the status of a seed-db task."""
    task = _seed_tasks.get(task_id)
    if not task:
        return {"error": "Task not found"}
    return task


# --- Crawl POIs from Intelligence ---

@router.post("/crawl-pois")
async def start_crawl_pois(request: CrawlPoisRequest, background_tasks: BackgroundTasks):
    """Extract POIs from city intelligence data (blogs + TripAdvisor)."""
    city = request.city.strip()
    if not city:
        return {"error": "City name is required."}

    if not request.include_blogs and not request.include_tripadvisor:
        return {"error": "At least one of include_blogs or include_tripadvisor must be true."}

    # Auto-detect country
    country = (request.country or "").strip()
    if not country:
        city_key = city.lower().replace(" ", "_")
        if city_key in CITY_BBOXES:
            country = CITY_BBOXES[city_key].get("country", "")

    task_id = str(uuid.uuid4())
    _crawl_poi_tasks[task_id] = {
        "task_id": task_id,
        "city": city,
        "country": country,
        "status": "started",
        "message": "POI extraction queued...",
        "total_inserted": 0,
        "blog_insights_found": 0,
        "tripadvisor_insights_found": 0,
        "blog_pois_converted": 0,
        "tripadvisor_pois_converted": 0,
        "blog_pois_inserted": 0,
        "tripadvisor_pois_inserted": 0,
        "duration_seconds": None,
        "error": None,
    }

    background_tasks.add_task(
        _run_crawl_pois, task_id, city, country,
        request.include_blogs, request.include_tripadvisor,
    )

    return {"task_id": task_id, "status": "started", "city": city, "country": country}


@router.get("/crawl-pois/{task_id}")
async def get_crawl_pois_status(task_id: str):
    """Poll the status of a crawl-pois task."""
    task = _crawl_poi_tasks.get(task_id)
    if not task:
        return {"error": "Task not found"}
    return task


# --- Auto-Discovery Web Crawl ---

async def _run_auto_crawl(
    task_id: str, city: str, country: str,
    include_open_web: bool, include_editorial: bool,
    include_blogs: bool, include_tripadvisor: bool,
):
    """Background task: Multi-source auto-discovery web crawl."""
    task = _auto_crawl_tasks[task_id]
    task["status"] = "running"
    task["message"] = f"Starting auto-discovery crawl for {city}..."
    start = time.time()

    try:
        from app.core.config import get_settings
        settings = get_settings()

        def progress_cb(stage, msg):
            task["stage"] = stage
            task["message"] = msg

        crawler = WebPOICrawler(
            google_api_key=settings.google_search_api_key,
            google_cx=settings.google_search_cx,
        )

        try:
            extracted_pois = await crawler.auto_crawl(
                city, country,
                include_open_web=include_open_web,
                include_editorial=include_editorial,
                include_blogs=include_blogs,
                include_tripadvisor=include_tripadvisor,
                progress_callback=progress_cb,
            )
        finally:
            await crawler.close()

        task["pois_extracted"] = len(extracted_pois)
        task["message"] = f"Converting {len(extracted_pois)} POIs..."

        # Convert to seed_pois format
        city_key = city.lower().replace(" ", "_")
        poi_dicts = convert_extracted_pois(extracted_pois, city_key, "auto_crawl")
        task["pois_converted"] = len(poi_dicts)

        # Insert into DB
        if poi_dicts:
            task["message"] = f"Inserting {len(poi_dicts)} POIs into database..."
            seed_data_dir = Path(__file__).resolve().parents[3] / "data" / "scripts"
            if str(seed_data_dir.parent.parent) not in sys.path:
                sys.path.insert(0, str(seed_data_dir.parent.parent))
            from data.scripts.seed_data import seed_pois

            async with AsyncSessionLocal() as session:
                inserted = await seed_pois(session, poi_dicts, city.title())
                task["pois_inserted"] = inserted
        else:
            task["pois_inserted"] = 0

        task["status"] = "completed"
        task["message"] = (
            f"Auto-crawl complete for {city}: "
            f"{task['pois_extracted']} extracted, {task['pois_inserted']} inserted"
        )
        task["duration_seconds"] = round(time.time() - start, 1)

    except Exception as e:
        logger.exception(f"Auto-crawl failed: {e}")
        task["status"] = "failed"
        task["error"] = str(e)
        task["message"] = f"Auto-crawl failed: {str(e)}"
        task["duration_seconds"] = round(time.time() - start, 1)


async def _run_url_crawl(task_id: str, urls: List[str], city: str, country: str):
    """Background task: URL-based POI extraction."""
    task = _url_crawl_tasks[task_id]
    task["status"] = "running"
    task["message"] = f"Starting URL crawl for {city} ({len(urls)} URLs)..."
    start = time.time()

    try:
        from app.core.config import get_settings
        settings = get_settings()

        def progress_cb(stage, msg):
            task["stage"] = stage
            task["message"] = msg

        crawler = WebPOICrawler(
            google_api_key=settings.google_search_api_key,
            google_cx=settings.google_search_cx,
        )

        try:
            extracted_pois = await crawler.url_crawl(
                urls, city, country,
                progress_callback=progress_cb,
            )
        finally:
            await crawler.close()

        task["pois_extracted"] = len(extracted_pois)
        task["message"] = f"Converting {len(extracted_pois)} POIs..."

        # Convert to seed_pois format
        city_key = city.lower().replace(" ", "_")
        poi_dicts = convert_extracted_pois(extracted_pois, city_key, "url_crawl")
        task["pois_converted"] = len(poi_dicts)

        # Insert into DB
        if poi_dicts:
            task["message"] = f"Inserting {len(poi_dicts)} POIs into database..."
            seed_data_dir = Path(__file__).resolve().parents[3] / "data" / "scripts"
            if str(seed_data_dir.parent.parent) not in sys.path:
                sys.path.insert(0, str(seed_data_dir.parent.parent))
            from data.scripts.seed_data import seed_pois

            async with AsyncSessionLocal() as session:
                inserted = await seed_pois(session, poi_dicts, city.title())
                task["pois_inserted"] = inserted
        else:
            task["pois_inserted"] = 0

        task["status"] = "completed"
        task["message"] = (
            f"URL crawl complete for {city}: "
            f"{task['pois_extracted']} extracted, {task['pois_inserted']} inserted"
        )
        task["duration_seconds"] = round(time.time() - start, 1)

    except Exception as e:
        logger.exception(f"URL crawl failed: {e}")
        task["status"] = "failed"
        task["error"] = str(e)
        task["message"] = f"URL crawl failed: {str(e)}"
        task["duration_seconds"] = round(time.time() - start, 1)


@router.post("/auto-crawl")
async def start_auto_crawl(request: AutoCrawlRequest, background_tasks: BackgroundTasks):
    """Trigger multi-source auto-discovery web crawl for a city."""
    city = request.city.strip()
    if not city:
        return {"error": "City name is required."}

    # Auto-detect country
    country = request.country.strip()
    if not country:
        city_key = city.lower().replace(" ", "_")
        if city_key in CITY_BBOXES:
            country = CITY_BBOXES[city_key].get("country", "")

    task_id = str(uuid.uuid4())
    _auto_crawl_tasks[task_id] = {
        "task_id": task_id,
        "city": city,
        "country": country,
        "status": "started",
        "stage": "queued",
        "message": "Auto-crawl queued...",
        "pois_extracted": 0,
        "pois_converted": 0,
        "pois_inserted": 0,
        "duration_seconds": None,
        "error": None,
    }

    background_tasks.add_task(
        _run_auto_crawl, task_id, city, country,
        request.include_open_web, request.include_editorial,
        request.include_blogs, request.include_tripadvisor,
    )

    return {"task_id": task_id, "status": "started", "city": city, "country": country}


@router.get("/auto-crawl/{task_id}")
async def get_auto_crawl_status(task_id: str):
    """Poll the status of an auto-crawl task."""
    task = _auto_crawl_tasks.get(task_id)
    if not task:
        return {"error": "Task not found"}
    return task


@router.post("/url-crawl")
async def start_url_crawl(request: UrlCrawlRequest, background_tasks: BackgroundTasks):
    """Trigger URL-based POI extraction."""
    if not request.urls:
        return {"error": "At least one URL is required."}

    city = request.city.strip()
    if not city:
        return {"error": "City name is required."}

    # Filter valid URLs
    urls = [u.strip() for u in request.urls if u.strip() and u.strip().startswith("http")]
    if not urls:
        return {"error": "No valid URLs provided. URLs must start with http:// or https://."}

    # Auto-detect country
    country = request.country.strip()
    if not country:
        city_key = city.lower().replace(" ", "_")
        if city_key in CITY_BBOXES:
            country = CITY_BBOXES[city_key].get("country", "")

    task_id = str(uuid.uuid4())
    _url_crawl_tasks[task_id] = {
        "task_id": task_id,
        "city": city,
        "country": country,
        "urls": urls,
        "status": "started",
        "stage": "queued",
        "message": "URL crawl queued...",
        "urls_count": len(urls),
        "pois_extracted": 0,
        "pois_converted": 0,
        "pois_inserted": 0,
        "duration_seconds": None,
        "error": None,
    }

    background_tasks.add_task(_run_url_crawl, task_id, urls, city, country)

    return {"task_id": task_id, "status": "started", "city": city, "urls_count": len(urls)}


@router.get("/url-crawl/{task_id}")
async def get_url_crawl_status(task_id: str):
    """Poll the status of a URL crawl task."""
    task = _url_crawl_tasks.get(task_id)
    if not task:
        return {"error": "Task not found"}
    return task


# --- Vector Search ---

@router.post("/search")
async def search_pois(request: SearchRequest, db: AsyncSession = Depends(get_db)):
    """Semantic vector search over POIs."""
    try:
        query_embedding = generate_embedding(request.query)

        stmt = (
            select(
                POI.id,
                POI.name,
                POI.description,
                POI.category,
                POI.subcategory,
                POI.city,
                POI.country,
                POI.address,
                POI.neighborhood,
                POI.latitude,
                POI.longitude,
                POI.cost_level,
                POI.typical_duration_minutes,
                (1 - POI.description_embedding.cosine_distance(query_embedding)).label("relevance_score"),
            )
            .where(POI.description_embedding.isnot(None))
        )

        if request.city:
            stmt = stmt.where(POI.city.ilike(f"%{request.city}%"))
        if request.category:
            stmt = stmt.where(POI.category.ilike(f"%{request.category}%"))

        stmt = stmt.order_by(POI.description_embedding.cosine_distance(query_embedding))
        stmt = stmt.limit(request.limit)

        result = await db.execute(stmt)
        rows = result.all()

        results = []
        for row in rows:
            results.append({
                "id": str(row.id),
                "name": row.name,
                "description": row.description,
                "category": row.category,
                "subcategory": row.subcategory,
                "city": row.city,
                "country": row.country,
                "address": row.address,
                "neighborhood": row.neighborhood,
                "latitude": float(row.latitude) if row.latitude else None,
                "longitude": float(row.longitude) if row.longitude else None,
                "cost_level": row.cost_level,
                "typical_duration_minutes": row.typical_duration_minutes,
                "relevance_score": round(float(row.relevance_score), 4) if row.relevance_score else 0.0,
            })

        return {"query": request.query, "results": results, "total": len(results)}
    except Exception as e:
        logger.warning(f"Search failed: {e}")
        return {"query": request.query, "results": [], "total": 0, "error": str(e)}
