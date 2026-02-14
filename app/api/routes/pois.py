from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import get_db
from app.models.poi import POI, POIPersonaScores, POIAttributes
from app.schemas.poi import (
    POICreate,
    POIUpdate,
    POIResponse,
    POIWithScoresResponse,
    POIPersonaScoresCreate,
    POIAttributesCreate,
    POISearchRequest,
    POISearchResponse,
    POISearchResult,
)
from app.services.data_ingestion.embeddings import EmbeddingService
from app.core.embeddings import create_poi_description_embedding, generate_embedding

router = APIRouter()


@router.get("/", response_model=List[POIWithScoresResponse])
async def list_pois(
    db: AsyncSession = Depends(get_db),
    city: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    neighborhood: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List all POIs with optional filtering."""
    stmt = select(POI).options(
        selectinload(POI.persona_scores),
        selectinload(POI.attributes),
    )

    if city:
        stmt = stmt.where(POI.city == city)
    if category:
        stmt = stmt.where(POI.category == category)
    if neighborhood:
        stmt = stmt.where(POI.neighborhood == neighborhood)

    stmt = stmt.offset(skip).limit(limit)

    result = await db.execute(stmt)
    pois = result.scalars().all()

    return pois


@router.post("/search", response_model=POISearchResponse)
async def search_pois(
    search_request: POISearchRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Search POIs using natural language queries with semantic similarity.

    Uses BGE embeddings and pgvector cosine similarity to find relevant POIs.
    """
    # Generate embedding for the query
    query_embedding = generate_embedding(search_request.query)

    # Build the base query with cosine distance
    # pgvector uses <=> for cosine distance (lower is better)
    # relevance_score = 1 - distance
    stmt = (
        select(
            POI,
            (1 - POI.description_embedding.cosine_distance(query_embedding)).label("relevance_score")
        )
        .options(
            selectinload(POI.persona_scores),
            selectinload(POI.attributes),
        )
        .where(POI.description_embedding.isnot(None))
    )

    # Apply filters
    if search_request.city:
        stmt = stmt.where(POI.city.ilike(f"%{search_request.city}%"))
    if search_request.category:
        stmt = stmt.where(POI.category.ilike(f"%{search_request.category}%"))
    if search_request.cost_level:
        stmt = stmt.where(POI.cost_level == search_request.cost_level)

    # Order by relevance (cosine distance ascending = most similar first)
    stmt = stmt.order_by(POI.description_embedding.cosine_distance(query_embedding))
    stmt = stmt.limit(search_request.limit)

    result = await db.execute(stmt)
    rows = result.all()

    # Convert to response format
    results = []
    for poi, relevance_score in rows:
        result_dict = {
            "id": poi.id,
            "name": poi.name,
            "description": poi.description,
            "latitude": poi.latitude,
            "longitude": poi.longitude,
            "address": poi.address,
            "neighborhood": poi.neighborhood,
            "city": poi.city,
            "country": poi.country,
            "category": poi.category,
            "subcategory": poi.subcategory,
            "typical_duration_minutes": poi.typical_duration_minutes,
            "best_time_of_day": poi.best_time_of_day,
            "best_days": poi.best_days,
            "seasonal_availability": poi.seasonal_availability,
            "cost_level": poi.cost_level,
            "avg_cost_per_person": poi.avg_cost_per_person,
            "cost_currency": poi.cost_currency,
            "source": poi.source,
            "source_id": poi.source_id,
            "created_at": poi.created_at,
            "updated_at": poi.updated_at,
            "relevance_score": float(relevance_score) if relevance_score else 0.0,
            "persona_scores": poi.persona_scores,
            "attributes": poi.attributes,
        }
        results.append(POISearchResult(**result_dict))

    return POISearchResponse(
        query=search_request.query,
        results=results,
        total=len(results),
    )


@router.get("/{poi_id}", response_model=POIWithScoresResponse)
async def get_poi(
    poi_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a single POI by ID."""
    stmt = (
        select(POI)
        .options(
            selectinload(POI.persona_scores),
            selectinload(POI.attributes),
        )
        .where(POI.id == poi_id)
    )

    result = await db.execute(stmt)
    poi = result.scalar_one_or_none()

    if not poi:
        raise HTTPException(status_code=404, detail="POI not found")

    return poi


@router.post("/", response_model=POIWithScoresResponse)
async def create_poi(
    poi_data: POICreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new POI."""
    # Create the POI
    poi = POI(
        name=poi_data.name,
        description=poi_data.description,
        latitude=poi_data.latitude,
        longitude=poi_data.longitude,
        address=poi_data.address,
        neighborhood=poi_data.neighborhood,
        city=poi_data.city,
        country=poi_data.country,
        category=poi_data.category,
        subcategory=poi_data.subcategory,
        typical_duration_minutes=poi_data.typical_duration_minutes,
        best_time_of_day=poi_data.best_time_of_day,
        best_days=poi_data.best_days,
        seasonal_availability=poi_data.seasonal_availability,
        cost_level=poi_data.cost_level,
        avg_cost_per_person=poi_data.avg_cost_per_person,
        cost_currency=poi_data.cost_currency,
        source=poi_data.source,
        source_id=poi_data.source_id,
    )

    # Generate embedding
    embedding = create_poi_description_embedding(
        name=poi.name,
        description=poi.description or "",
        category=poi.category or "",
        subcategory=poi.subcategory or "",
        neighborhood=poi.neighborhood or "",
    )
    poi.description_embedding = embedding

    db.add(poi)
    await db.flush()

    # Create persona scores if provided
    if poi_data.persona_scores:
        scores = POIPersonaScores(
            poi_id=poi.id,
            **poi_data.persona_scores.model_dump(),
        )
        db.add(scores)

    # Create attributes if provided
    if poi_data.attributes:
        attrs = POIAttributes(
            poi_id=poi.id,
            **poi_data.attributes.model_dump(),
        )
        db.add(attrs)

    await db.commit()

    # Reload with relationships
    stmt = (
        select(POI)
        .options(
            selectinload(POI.persona_scores),
            selectinload(POI.attributes),
        )
        .where(POI.id == poi.id)
    )
    result = await db.execute(stmt)
    return result.scalar_one()


@router.patch("/{poi_id}", response_model=POIWithScoresResponse)
async def update_poi(
    poi_id: UUID,
    poi_data: POIUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing POI."""
    stmt = select(POI).where(POI.id == poi_id)
    result = await db.execute(stmt)
    poi = result.scalar_one_or_none()

    if not poi:
        raise HTTPException(status_code=404, detail="POI not found")

    # Update fields
    update_data = poi_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(poi, field, value)

    # Regenerate embedding if name or description changed
    if "name" in update_data or "description" in update_data:
        embedding = create_poi_description_embedding(
            name=poi.name,
            description=poi.description or "",
            category=poi.category or "",
            subcategory=poi.subcategory or "",
            neighborhood=poi.neighborhood or "",
        )
        poi.description_embedding = embedding

    await db.commit()

    # Reload with relationships
    stmt = (
        select(POI)
        .options(
            selectinload(POI.persona_scores),
            selectinload(POI.attributes),
        )
        .where(POI.id == poi.id)
    )
    result = await db.execute(stmt)
    return result.scalar_one()


@router.delete("/{poi_id}")
async def delete_poi(
    poi_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete a POI."""
    stmt = select(POI).where(POI.id == poi_id)
    result = await db.execute(stmt)
    poi = result.scalar_one_or_none()

    if not poi:
        raise HTTPException(status_code=404, detail="POI not found")

    await db.delete(poi)
    await db.commit()

    return {"status": "deleted", "id": str(poi_id)}


@router.put("/{poi_id}/scores", response_model=POIWithScoresResponse)
async def update_poi_scores(
    poi_id: UUID,
    scores_data: POIPersonaScoresCreate,
    db: AsyncSession = Depends(get_db),
):
    """Update persona scores for a POI."""
    # Check POI exists
    stmt = select(POI).where(POI.id == poi_id)
    result = await db.execute(stmt)
    poi = result.scalar_one_or_none()

    if not poi:
        raise HTTPException(status_code=404, detail="POI not found")

    # Get or create scores
    stmt = select(POIPersonaScores).where(POIPersonaScores.poi_id == poi_id)
    result = await db.execute(stmt)
    scores = result.scalar_one_or_none()

    if scores:
        # Update existing
        for field, value in scores_data.model_dump().items():
            setattr(scores, field, value)
    else:
        # Create new
        scores = POIPersonaScores(poi_id=poi_id, **scores_data.model_dump())
        db.add(scores)

    await db.commit()

    # Reload with relationships
    stmt = (
        select(POI)
        .options(
            selectinload(POI.persona_scores),
            selectinload(POI.attributes),
        )
        .where(POI.id == poi_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one()


@router.put("/{poi_id}/attributes", response_model=POIWithScoresResponse)
async def update_poi_attributes(
    poi_id: UUID,
    attrs_data: POIAttributesCreate,
    db: AsyncSession = Depends(get_db),
):
    """Update attributes for a POI."""
    # Check POI exists
    stmt = select(POI).where(POI.id == poi_id)
    result = await db.execute(stmt)
    poi = result.scalar_one_or_none()

    if not poi:
        raise HTTPException(status_code=404, detail="POI not found")

    # Get or create attributes
    stmt = select(POIAttributes).where(POIAttributes.poi_id == poi_id)
    result = await db.execute(stmt)
    attrs = result.scalar_one_or_none()

    if attrs:
        # Update existing
        for field, value in attrs_data.model_dump().items():
            setattr(attrs, field, value)
    else:
        # Create new
        attrs = POIAttributes(poi_id=poi_id, **attrs_data.model_dump())
        db.add(attrs)

    await db.commit()

    # Reload with relationships
    stmt = (
        select(POI)
        .options(
            selectinload(POI.persona_scores),
            selectinload(POI.attributes),
        )
        .where(POI.id == poi_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one()


@router.post("/generate-embeddings")
async def generate_all_embeddings(
    db: AsyncSession = Depends(get_db),
):
    """Generate embeddings for all POIs without them."""
    service = EmbeddingService(db)
    count = await service.generate_all_embeddings()
    return {"status": "success", "embeddings_generated": count}
