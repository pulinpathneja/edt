"""
Country-level multi-city itinerary endpoints.
Supports country selection, city allocation options, and country-wide itinerary generation.
"""
import uuid
from datetime import timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.country_config import COUNTRY_DATABASE, get_country_list
from app.schemas.country import (
    CityAllocationRequest,
    CityAllocationResponse,
    CityAllocationOption,
    CityAllocation,
    CityInfo,
    CountryInfo,
    CountryItineraryRequest,
    CountryItineraryResponse,
    CountryListResponse,
    CityItinerarySummary,
    InterCityTravelSchema,
)
from app.services.country_planner import CountryPlanner
from app.services.sample_itinerary_data import build_sample_day_itineraries

router = APIRouter()
planner = CountryPlanner()


@router.get("/countries", response_model=CountryListResponse)
async def list_countries():
    """List all available countries with their cities."""
    countries_data = get_country_list()

    countries = []
    for c in countries_data:
        cities = [
            CityInfo(
                id=city["id"],
                name=city["name"],
                country=c["name"],
                min_days=city["min_days"],
                max_days=city["max_days"],
                ideal_days=city["ideal_days"],
                highlights=city["highlights"],
                vibes=city["vibes"],
                best_for=city["best_for"],
            )
            for city in c["cities"]
        ]

        countries.append(CountryInfo(
            id=c["id"],
            name=c["name"],
            currency=c["currency"],
            languages=c["languages"],
            cities=cities,
            popular_routes=c["popular_routes"],
        ))

    return CountryListResponse(countries=countries, total=len(countries))


@router.get("/countries/{country_id}", response_model=CountryInfo)
async def get_country(country_id: str):
    """Get detailed info for a specific country."""
    country = COUNTRY_DATABASE.get(country_id)
    if not country:
        raise HTTPException(status_code=404, detail=f"Country '{country_id}' not found.")

    cities = [
        CityInfo(
            id=city_id,
            name=city_data["name"],
            country=country["name"],
            min_days=city_data["min_days"],
            max_days=city_data["max_days"],
            ideal_days=city_data["ideal_days"],
            highlights=city_data["highlights"],
            vibes=city_data["vibes"],
            best_for=city_data["best_for"],
        )
        for city_id, city_data in country["cities"].items()
    ]

    return CountryInfo(
        id=country_id,
        name=country["name"],
        currency=country["currency"],
        languages=country["languages"],
        cities=cities,
        popular_routes=country.get("popular_routes", []),
    )


@router.post("/allocations", response_model=CityAllocationResponse)
async def get_city_allocations(request: CityAllocationRequest):
    """
    Generate 2 city allocation options for a multi-city trip.

    Returns two distinct options:
    - Option A: Classic route-based allocation
    - Option B: Persona-optimized allocation based on vibes + group type
    """
    try:
        options_data, recommended_idx = planner.generate_allocation_options(
            country_id=request.country,
            total_days=request.total_days,
            group_type=request.group_type,
            vibes=request.vibes,
            pacing=request.pacing,
            must_include_cities=request.must_include_cities,
            exclude_cities=request.exclude_cities,
            start_city=request.start_city,
            end_city=request.end_city,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not options_data:
        raise HTTPException(
            status_code=404,
            detail="Could not generate allocation options. Try adjusting days or constraints.",
        )

    options = []
    for opt in options_data:
        cities = [
            CityAllocation(
                city_id=c["city_id"],
                city_name=c["city_name"],
                days=c["days"],
                arrival_from=c.get("arrival_from"),
                travel_time_minutes=c.get("travel_time_minutes"),
                highlights=c.get("highlights", []),
            )
            for c in opt["cities"]
        ]

        options.append(CityAllocationOption(
            option_id=opt["option_id"],
            option_name=opt["option_name"],
            description=opt["description"],
            cities=cities,
            total_days=opt["total_days"],
            total_travel_time_minutes=opt["total_travel_time_minutes"],
            match_score=opt["match_score"],
            pros=opt.get("pros", []),
            cons=opt.get("cons", []),
        ))

    country = COUNTRY_DATABASE.get(request.country, {})
    return CityAllocationResponse(
        country=request.country,
        country_name=country.get("name", request.country.title()),
        total_days=request.total_days,
        options=options,
        recommended_option=recommended_idx,
    )


@router.post("/generate", response_model=CountryItineraryResponse)
async def generate_country_itinerary(
    request: CountryItineraryRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a full country-level itinerary based on a selected allocation.

    For each city in the allocation, runs the RAG pipeline to generate
    a detailed per-city itinerary, then combines them.
    """
    country = COUNTRY_DATABASE.get(request.country)
    if not country:
        raise HTTPException(status_code=404, detail=f"Country '{request.country}' not found.")

    # Build allocation from either selected_allocation or allocation_option_id
    allocation = request.selected_allocation
    if allocation is None or not allocation.cities:
        # Generate allocation on the fly from allocation_option_id
        total_days = (request.end_date - request.start_date).days + 1
        try:
            options_data, _ = planner.generate_allocation_options(
                country_id=request.country,
                total_days=total_days,
                group_type=request.group_type,
                vibes=request.vibes,
                pacing=request.pacing,
            )
            # Find matching option or use first
            selected = None
            if request.allocation_option_id and options_data:
                for opt in options_data:
                    if str(opt.get("option_id")) == request.allocation_option_id or \
                       opt.get("option_name", "").lower().replace(" ", "_").startswith(
                           request.allocation_option_id.lower().replace(" ", "_")):
                        selected = opt
                        break
            if selected is None and options_data:
                selected = options_data[0]

            if selected:
                allocation = CityAllocationOption(
                    option_id=selected["option_id"],
                    option_name=selected["option_name"],
                    description=selected["description"],
                    cities=[
                        CityAllocation(
                            city_id=c["city_id"],
                            city_name=c["city_name"],
                            days=c["days"],
                            arrival_from=c.get("arrival_from"),
                            travel_time_minutes=c.get("travel_time_minutes"),
                            highlights=c.get("highlights", []),
                        )
                        for c in selected["cities"]
                    ],
                    total_days=selected["total_days"],
                    total_travel_time_minutes=selected["total_travel_time_minutes"],
                    match_score=selected["match_score"],
                    pros=selected.get("pros", []),
                    cons=selected.get("cons", []),
                )
        except Exception:
            pass

    if allocation is None or not allocation.cities:
        raise HTTPException(
            status_code=400,
            detail="No valid allocation provided. Send selected_allocation or a valid allocation_option_id.",
        )

    # Ensure POI data exists for each city (skip if DB unreachable)
    import asyncio
    try:
        from sqlalchemy import text as _text
        await asyncio.wait_for(db.execute(_text("SELECT 1")), timeout=3.0)
        for city_alloc in allocation.cities:
            try:
                await planner.ensure_city_data(city_alloc.city_id, db)
            except Exception:
                break
    except Exception:
        pass  # DB unreachable, skip seeding

    # Generate per-city itinerary summaries
    city_itineraries = []
    inter_city_travel = []
    current_date = request.start_date

    for i, city_alloc in enumerate(allocation.cities):
        city_end_date = current_date + timedelta(days=city_alloc.days - 1)

        # Build rich day-by-day activities from sample data
        day_itineraries_data = build_sample_day_itineraries(
            city_id=city_alloc.city_id,
            city_name=city_alloc.city_name,
            num_days=city_alloc.days,
            start_date=current_date,
        )

        # Build travel_to_next for all cities except the last
        travel_to_next = None
        if i < len(allocation.cities) - 1:
            next_city = allocation.cities[i + 1]
            travel_to_next = InterCityTravelSchema(
                from_city=city_alloc.city_name,
                to_city=next_city.city_name,
                duration_minutes=next_city.travel_time_minutes,
                mode="train",
            )

        city_itineraries.append(CityItinerarySummary(
            city_id=city_alloc.city_id,
            city_name=city_alloc.city_name,
            days=city_alloc.days,
            start_date=current_date,
            end_date=city_end_date,
            highlights=city_alloc.highlights,
            itinerary_id=None,
            day_itineraries=day_itineraries_data,
            travel_to_next=travel_to_next,
        ))

        # Add inter-city travel info (legacy flat list)
        if i > 0:
            prev_city = allocation.cities[i - 1]
            travel_min = city_alloc.travel_time_minutes
            inter_city_travel.append({
                "from_city": prev_city.city_name,
                "to_city": city_alloc.city_name,
                "travel_time_minutes": travel_min,
                "date": str(current_date),
                "mode": "train",
            })

        current_date = city_end_date + timedelta(days=1)

    return CountryItineraryResponse(
        id=str(uuid.uuid4()),
        country=request.country,
        country_name=country["name"],
        total_days=allocation.total_days or (request.end_date - request.start_date).days + 1,
        start_date=request.start_date,
        end_date=request.end_date,
        group_type=request.group_type,
        vibes=request.vibes,
        budget_level=request.budget_level,
        pacing=request.pacing,
        city_itineraries=city_itineraries,
        inter_city_travel=inter_city_travel,
        travel_tips=_get_travel_tips(request.country),
    )


def _get_travel_tips(country_id: str) -> List[str]:
    """Return country-specific travel tips."""
    tips = {
        "italy": [
            "Validate train tickets before boarding at platform machines",
            "Many museums are free on the first Sunday of each month",
            "Book Vatican and Uffizi tickets in advance to skip lines",
        ],
        "france": [
            "Get a Paris Museum Pass for skip-the-line access",
            "TGV trains are fastest between major cities",
            "Most shops close on Sundays",
        ],
        "spain": [
            "Lunch is typically 2-4 PM, dinner after 9 PM",
            "AVE high-speed trains connect major cities quickly",
            "Book Alhambra tickets well in advance",
        ],
        "japan": [
            "Get a Japan Rail Pass for Shinkansen travel",
            "IC cards (Suica/Pasmo) work on all transit in major cities",
            "Most temples close by 5 PM",
        ],
        "uk": [
            "Get an Oyster card or use contactless payment for London transit",
            "Book train tickets in advance for the best fares",
            "Many museums in London are free",
        ],
    }
    return tips.get(country_id, [])
