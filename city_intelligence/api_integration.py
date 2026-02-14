"""
API Integration for City Intelligence
=====================================

This module provides FastAPI endpoints to integrate city intelligence
generation with the EDT API. Add these routes to your FastAPI app.

Usage:
------
from fastapi import FastAPI
from city_intelligence.api_integration import router as city_intel_router

app = FastAPI()
app.include_router(city_intel_router, prefix="/api/v1/city-intelligence")
"""

import asyncio
import os
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional
from pathlib import Path

router = APIRouter(tags=["City Intelligence"])


class CityIntelRequest(BaseModel):
    city_name: str
    force_refresh: bool = False


class CityIntelResponse(BaseModel):
    city_name: str
    status: str
    message: str
    report_path: Optional[str] = None
    summary_path: Optional[str] = None


# Track generation status
generation_status = {}


def _get_output_dir() -> Path:
    """Get the output directory for city intelligence files."""
    base_dir = os.getenv("CITY_INTEL_OUTPUT_DIR", "city_intelligence/cities")
    path = Path(base_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _get_city_file_paths(city: str) -> tuple[Path, Path]:
    """Get the file paths for a city's intelligence files."""
    output_dir = _get_output_dir()
    city_slug = city.lower().replace(" ", "_")
    json_path = output_dir / f"{city_slug}_intelligence.json"
    md_path = output_dir / f"{city_slug}_summary.md"
    return json_path, md_path


async def _generate_city_intelligence_task(city: str):
    """Background task to generate city intelligence."""
    from .generator import generate_city_report

    try:
        generation_status[city] = "in_progress"

        viator_key = os.getenv("VIATOR_API_KEY", "")
        gyg_key = os.getenv("GYG_API_KEY", "")
        eventbrite_token = os.getenv("EVENTBRITE_TOKEN", "")

        await generate_city_report(
            city,
            output_dir=str(_get_output_dir()),
            viator_key=viator_key,
            gyg_key=gyg_key,
            eventbrite_token=eventbrite_token
        )

        generation_status[city] = "completed"

    except Exception as e:
        generation_status[city] = f"failed: {str(e)}"
        raise


@router.post("/generate", response_model=CityIntelResponse)
async def generate_city_intelligence(
    request: CityIntelRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate city intelligence report.

    This endpoint triggers the generation of a comprehensive city intelligence
    report including Reddit data, tour information, and persona-specific
    recommendations.

    The generation runs in the background. Use /status/{city_name} to check progress.
    """
    city = request.city_name
    json_path, md_path = _get_city_file_paths(city)

    # Check if already exists and not forcing refresh
    if json_path.exists() and not request.force_refresh:
        return CityIntelResponse(
            city_name=city,
            status="exists",
            message="Intelligence report already exists. Use force_refresh=true to regenerate.",
            report_path=str(json_path),
            summary_path=str(md_path) if md_path.exists() else None,
        )

    # Check if generation is already in progress
    if city in generation_status and generation_status[city] == "in_progress":
        return CityIntelResponse(
            city_name=city,
            status="in_progress",
            message="Generation already in progress. Check /status/{city_name} for updates.",
        )

    # Start background generation
    background_tasks.add_task(_generate_city_intelligence_task, city)

    return CityIntelResponse(
        city_name=city,
        status="started",
        message="City intelligence generation started. Check /status/{city_name} for progress.",
    )


@router.get("/status/{city_name}", response_model=CityIntelResponse)
async def get_generation_status(city_name: str):
    """
    Check the status of city intelligence generation.
    """
    json_path, md_path = _get_city_file_paths(city_name)

    # Check if completed (file exists)
    if json_path.exists():
        return CityIntelResponse(
            city_name=city_name,
            status="completed",
            message="City intelligence report is ready.",
            report_path=str(json_path),
            summary_path=str(md_path) if md_path.exists() else None,
        )

    # Check generation status
    status = generation_status.get(city_name, "not_started")

    if status == "in_progress":
        return CityIntelResponse(
            city_name=city_name,
            status="in_progress",
            message="Generation is in progress...",
        )
    elif status.startswith("failed"):
        return CityIntelResponse(
            city_name=city_name,
            status="failed",
            message=status,
        )
    else:
        return CityIntelResponse(
            city_name=city_name,
            status="not_found",
            message="No intelligence report found. Use /generate to create one.",
        )


@router.get("/report/{city_name}")
async def get_city_report(city_name: str):
    """
    Get the city intelligence report.

    Returns the full JSON report for a city.
    """
    import json

    json_path, _ = _get_city_file_paths(city_name)

    if not json_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"No intelligence report found for {city_name}. Generate one first."
        )

    with open(json_path) as f:
        return json.load(f)


@router.get("/summary/{city_name}")
async def get_city_summary(city_name: str):
    """
    Get the city intelligence summary.

    Returns a simplified summary suitable for display.
    """
    import json

    json_path, _ = _get_city_file_paths(city_name)

    if not json_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"No intelligence report found for {city_name}. Generate one first."
        )

    with open(json_path) as f:
        data = json.load(f)

    # Return simplified summary
    return {
        "city_name": data["city_name"],
        "generated_at": data["generated_at"],
        "summary": data["summary"],
        "persona_insights": {
            persona: {
                "name": insights["persona_name"],
                "key_tips": insights["key_tips"][:5],
                "things_to_avoid": insights["things_to_avoid"][:3],
            }
            for persona, insights in data.get("persona_insights", {}).items()
        },
        "search_urls": data.get("search_urls", {}),
    }


@router.get("/personas/{city_name}/{persona_id}")
async def get_persona_insights(city_name: str, persona_id: str):
    """
    Get insights for a specific persona in a city.

    Valid persona IDs:
    - solo_traveler
    - couple
    - family
    - budget
    - luxury
    - adventure
    - foodie
    - culture
    """
    import json

    json_path, _ = _get_city_file_paths(city_name)

    if not json_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"No intelligence report found for {city_name}. Generate one first."
        )

    with open(json_path) as f:
        data = json.load(f)

    persona_insights = data.get("persona_insights", {})

    if persona_id not in persona_insights:
        raise HTTPException(
            status_code=404,
            detail=f"Persona '{persona_id}' not found. Valid personas: {list(persona_insights.keys())}"
        )

    return {
        "city_name": city_name,
        "persona": persona_insights[persona_id],
        "related_tours": data.get("tours_events", {}).get("walking_tours", [])[:5],
    }


@router.get("/available")
async def list_available_cities():
    """
    List all cities with available intelligence reports.
    """
    output_dir = _get_output_dir()

    cities = []
    for file in output_dir.glob("*_intelligence.json"):
        city_slug = file.stem.replace("_intelligence", "")
        city_name = city_slug.replace("_", " ").title()
        cities.append({
            "city_name": city_name,
            "city_slug": city_slug,
            "report_path": str(file),
        })

    return {"cities": cities, "count": len(cities)}
