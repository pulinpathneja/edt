"""
City Intelligence API Service
=============================

FastAPI service for generating city travel intelligence.
Deployed on Cloud Run.

Usage:
    POST /crawl {"city": "Toronto"}
    GET /status/{city}
    GET /report/{city}
"""

import asyncio
import os
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
from datetime import datetime
import json

# Initialize FastAPI app
app = FastAPI(
    title="City Intelligence API",
    description="Generate travel intelligence for cities by crawling Reddit, tour platforms, and more.",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Output directory
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "/tmp/city_intelligence"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Track generation status
generation_status = {}


class CrawlRequest(BaseModel):
    city: str
    force_refresh: bool = False


class CrawlResponse(BaseModel):
    city: str
    status: str
    message: str
    report_url: Optional[str] = None


def get_city_paths(city: str) -> tuple[Path, Path]:
    """Get file paths for a city."""
    city_slug = city.lower().replace(" ", "_")
    json_path = OUTPUT_DIR / f"{city_slug}_intelligence.json"
    md_path = OUTPUT_DIR / f"{city_slug}_summary.md"
    return json_path, md_path


async def run_city_crawl(city: str):
    """Background task to crawl city data."""
    from reddit_scraper import collect_city_intelligence
    from tours_events import collect_tours_events, WebSearchTours
    from generator import CityIntelligenceGenerator

    try:
        generation_status[city] = {
            "status": "in_progress",
            "started_at": datetime.utcnow().isoformat(),
            "stage": "Starting...",
        }

        print(f"\n{'='*60}")
        print(f"Starting crawl for: {city}")
        print(f"{'='*60}")

        # Stage 1: Reddit
        generation_status[city]["stage"] = "Crawling Reddit..."
        print("\n[1/3] Crawling Reddit...")
        reddit_data = await collect_city_intelligence(city)
        print(f"  Collected {len(reddit_data.posts)} posts from Reddit")

        # Stage 2: Tours
        generation_status[city]["stage"] = "Fetching tours..."
        print("\n[2/3] Fetching tours and events...")
        tours_data = await collect_tours_events(city)
        print(f"  Found {len(tours_data.walking_tours)} walking tours")

        # Stage 3: Generate report
        generation_status[city]["stage"] = "Generating report..."
        print("\n[3/3] Generating intelligence report...")

        generator = CityIntelligenceGenerator(str(OUTPUT_DIR))
        report = await generator.generate_report(city, save_to_file=True)

        generation_status[city] = {
            "status": "completed",
            "completed_at": datetime.utcnow().isoformat(),
            "reddit_posts": len(reddit_data.posts),
            "tours_found": len(tours_data.walking_tours) + len(tours_data.food_tours),
        }

        print(f"\n✓ Crawl completed for {city}")

    except Exception as e:
        print(f"\n✗ Error crawling {city}: {e}")
        generation_status[city] = {
            "status": "failed",
            "error": str(e),
            "failed_at": datetime.utcnow().isoformat(),
        }
        raise


@app.get("/")
async def root():
    """API root - shows available endpoints."""
    return {
        "service": "City Intelligence API",
        "version": "1.0.0",
        "endpoints": {
            "POST /crawl": "Start crawling a city",
            "GET /status/{city}": "Check crawl status",
            "GET /report/{city}": "Get full intelligence report",
            "GET /summary/{city}": "Get summary for a city",
            "GET /cities": "List all crawled cities",
        },
        "example": {
            "crawl": "POST /crawl with body: {\"city\": \"Toronto\"}",
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.post("/crawl", response_model=CrawlResponse)
async def crawl_city(request: CrawlRequest, background_tasks: BackgroundTasks):
    """
    Start crawling a city for travel intelligence.

    This will:
    1. Crawl Reddit for local insights, tips, and reviews
    2. Fetch walking tours and events from various platforms
    3. Generate persona-specific recommendations
    4. Create a comprehensive intelligence report

    The crawl runs in the background. Use /status/{city} to check progress.
    """
    city = request.city.strip()

    if not city:
        raise HTTPException(status_code=400, detail="City name is required")

    json_path, _ = get_city_paths(city)

    # Check if already exists
    if json_path.exists() and not request.force_refresh:
        return CrawlResponse(
            city=city,
            status="exists",
            message=f"Intelligence report already exists for {city}. Use force_refresh=true to regenerate.",
            report_url=f"/report/{city.lower().replace(' ', '_')}",
        )

    # Check if crawl is in progress
    if city in generation_status:
        status = generation_status[city].get("status")
        if status == "in_progress":
            stage = generation_status[city].get("stage", "Processing...")
            return CrawlResponse(
                city=city,
                status="in_progress",
                message=f"Crawl already in progress: {stage}",
            )

    # Start background crawl
    background_tasks.add_task(run_city_crawl, city)

    return CrawlResponse(
        city=city,
        status="started",
        message=f"Started crawling {city}. This takes 2-5 minutes. Check /status/{city.lower().replace(' ', '_')} for progress.",
    )


@app.get("/status/{city_slug}")
async def get_status(city_slug: str):
    """
    Check the status of a city crawl.
    """
    city = city_slug.replace("_", " ").title()
    json_path, _ = get_city_paths(city)

    # Check if file exists (completed)
    if json_path.exists():
        with open(json_path) as f:
            data = json.load(f)

        return {
            "city": city,
            "status": "completed",
            "generated_at": data.get("generated_at"),
            "summary": data.get("summary", {}),
            "report_url": f"/report/{city_slug}",
        }

    # Check in-progress status
    if city in generation_status:
        return {
            "city": city,
            **generation_status[city],
        }

    return {
        "city": city,
        "status": "not_found",
        "message": "No crawl found. Use POST /crawl to start one.",
    }


@app.get("/report/{city_slug}")
async def get_report(city_slug: str):
    """
    Get the full intelligence report for a city.
    """
    city = city_slug.replace("_", " ").title()
    json_path, _ = get_city_paths(city)

    if not json_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"No report found for {city}. Use POST /crawl to generate one.",
        )

    with open(json_path) as f:
        return json.load(f)


@app.get("/summary/{city_slug}")
async def get_summary(city_slug: str):
    """
    Get a simplified summary for a city.
    """
    city = city_slug.replace("_", " ").title()
    json_path, _ = get_city_paths(city)

    if not json_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"No report found for {city}. Use POST /crawl to generate one.",
        )

    with open(json_path) as f:
        data = json.load(f)

    return {
        "city": data["city_name"],
        "generated_at": data["generated_at"],
        "summary": data["summary"],
        "top_highlights": data["summary"].get("top_highlights", []),
        "personas": list(data.get("persona_insights", {}).keys()),
        "search_urls": data.get("search_urls", {}),
    }


@app.get("/personas/{city_slug}")
async def get_personas(city_slug: str):
    """
    Get persona-specific insights for a city.
    """
    city = city_slug.replace("_", " ").title()
    json_path, _ = get_city_paths(city)

    if not json_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"No report found for {city}. Use POST /crawl to generate one.",
        )

    with open(json_path) as f:
        data = json.load(f)

    return {
        "city": city,
        "personas": data.get("persona_insights", {}),
    }


@app.get("/personas/{city_slug}/{persona_id}")
async def get_persona(city_slug: str, persona_id: str):
    """
    Get insights for a specific persona.

    Valid personas: solo_traveler, couple, family, budget, luxury, adventure, foodie, culture
    """
    city = city_slug.replace("_", " ").title()
    json_path, _ = get_city_paths(city)

    if not json_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"No report found for {city}. Use POST /crawl to generate one.",
        )

    with open(json_path) as f:
        data = json.load(f)

    personas = data.get("persona_insights", {})

    if persona_id not in personas:
        raise HTTPException(
            status_code=404,
            detail=f"Persona '{persona_id}' not found. Valid: {list(personas.keys())}",
        )

    return {
        "city": city,
        "persona": personas[persona_id],
    }


@app.get("/cities")
async def list_cities():
    """
    List all cities with available intelligence reports.
    """
    cities = []

    for file in OUTPUT_DIR.glob("*_intelligence.json"):
        city_slug = file.stem.replace("_intelligence", "")
        city_name = city_slug.replace("_", " ").title()

        with open(file) as f:
            data = json.load(f)

        cities.append({
            "city": city_name,
            "slug": city_slug,
            "generated_at": data.get("generated_at"),
            "reddit_posts": data.get("summary", {}).get("data_sources", {}).get("reddit_posts", 0),
            "report_url": f"/report/{city_slug}",
        })

    return {
        "cities": cities,
        "total": len(cities),
    }


@app.delete("/report/{city_slug}")
async def delete_report(city_slug: str):
    """
    Delete a city intelligence report.
    """
    city = city_slug.replace("_", " ").title()
    json_path, md_path = get_city_paths(city)

    deleted = []

    if json_path.exists():
        json_path.unlink()
        deleted.append(str(json_path))

    if md_path.exists():
        md_path.unlink()
        deleted.append(str(md_path))

    if city in generation_status:
        del generation_status[city]

    if not deleted:
        raise HTTPException(status_code=404, detail=f"No report found for {city}")

    return {
        "city": city,
        "status": "deleted",
        "files_removed": deleted,
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
