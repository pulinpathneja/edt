from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import get_db
from app.models.itinerary import TripRequest, Itinerary, ItineraryDay, ItineraryItem
from app.models.poi import POI
from app.schemas.itinerary import (
    TripRequestCreate,
    TripRequestResponse,
    ItineraryResponse,
    GenerateItineraryRequest,
)
from app.services.rag import POIRetriever, PersonaScorer, ItineraryAssembler
from app.services.rag.scorer import POIFilter

router = APIRouter()


@router.post("/generate", response_model=ItineraryResponse)
async def generate_itinerary(
    request: GenerateItineraryRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a personalized itinerary using the RAG pipeline.

    This is the main endpoint that orchestrates:
    1. Semantic retrieval of POI candidates
    2. Persona-based scoring
    3. Itinerary assembly with pacing
    """
    trip_request = request.trip_request

    # Phase 1: Retrieve POI candidates
    retriever = POIRetriever(db)
    candidates = await retriever.retrieve_candidates(
        trip_request=trip_request,
        limit=100,
        exclude_poi_ids=request.exclude_pois,
    )

    if not candidates:
        raise HTTPException(
            status_code=404,
            detail="No POIs found matching your criteria. Try adjusting filters.",
        )

    # Phase 2: Score candidates by persona
    scorer = PersonaScorer()
    scored_pois = scorer.score_candidates(candidates, trip_request)

    # Apply hard filters
    filtered_pois = POIFilter.apply_filters(scored_pois, trip_request)

    if not filtered_pois:
        raise HTTPException(
            status_code=404,
            detail="No POIs passed the filters. Try relaxing constraints.",
        )

    # Phase 3: Assemble itinerary
    assembler = ItineraryAssembler(pacing=trip_request.pacing)
    itinerary = assembler.build_itinerary(
        scored_pois=filtered_pois,
        trip_request=trip_request,
        must_include_ids=request.must_include_pois,
    )

    # Save trip request and itinerary to database
    db_trip_request = TripRequest(**trip_request.model_dump())
    db.add(db_trip_request)
    await db.flush()

    itinerary.trip_request_id = db_trip_request.id

    # Save itinerary
    db.add(itinerary)
    for day in itinerary.days:
        day.itinerary_id = itinerary.id
        db.add(day)
        for item in day.items:
            item.itinerary_day_id = day.id
            db.add(item)

    await db.commit()

    # Reload with relationships for response
    stmt = (
        select(Itinerary)
        .options(
            selectinload(Itinerary.days).selectinload(ItineraryDay.items).selectinload(ItineraryItem.poi),
        )
        .where(Itinerary.id == itinerary.id)
    )
    result = await db.execute(stmt)
    saved_itinerary = result.scalar_one()

    return saved_itinerary


@router.get("/", response_model=List[ItineraryResponse])
async def list_itineraries(
    db: AsyncSession = Depends(get_db),
    user_id: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
):
    """List itineraries, optionally filtered by user."""
    stmt = (
        select(Itinerary)
        .options(
            selectinload(Itinerary.days).selectinload(ItineraryDay.items).selectinload(ItineraryItem.poi),
        )
    )

    if user_id:
        stmt = stmt.join(TripRequest).where(TripRequest.user_id == user_id)

    stmt = stmt.order_by(Itinerary.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(stmt)
    itineraries = result.scalars().all()

    return itineraries


@router.get("/{itinerary_id}", response_model=ItineraryResponse)
async def get_itinerary(
    itinerary_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a single itinerary by ID."""
    stmt = (
        select(Itinerary)
        .options(
            selectinload(Itinerary.days).selectinload(ItineraryDay.items).selectinload(ItineraryItem.poi),
        )
        .where(Itinerary.id == itinerary_id)
    )

    result = await db.execute(stmt)
    itinerary = result.scalar_one_or_none()

    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary not found")

    return itinerary


@router.delete("/{itinerary_id}")
async def delete_itinerary(
    itinerary_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete an itinerary."""
    stmt = select(Itinerary).where(Itinerary.id == itinerary_id)
    result = await db.execute(stmt)
    itinerary = result.scalar_one_or_none()

    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary not found")

    await db.delete(itinerary)
    await db.commit()

    return {"status": "deleted", "id": str(itinerary_id)}


@router.get("/requests/", response_model=List[TripRequestResponse])
async def list_trip_requests(
    db: AsyncSession = Depends(get_db),
    user_id: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
):
    """List trip requests."""
    stmt = select(TripRequest)

    if user_id:
        stmt = stmt.where(TripRequest.user_id == user_id)

    stmt = stmt.order_by(TripRequest.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(stmt)
    requests = result.scalars().all()

    return requests


@router.get("/requests/{request_id}", response_model=TripRequestResponse)
async def get_trip_request(
    request_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a single trip request by ID."""
    stmt = select(TripRequest).where(TripRequest.id == request_id)
    result = await db.execute(stmt)
    trip_request = result.scalar_one_or_none()

    if not trip_request:
        raise HTTPException(status_code=404, detail="Trip request not found")

    return trip_request
