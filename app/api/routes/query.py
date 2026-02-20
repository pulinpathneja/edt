"""
Natural language query endpoint for resolving travel queries against the vector DB.

Examples:
  - "romantic restaurant in rome"
  - "hidden gems in tokyo"
  - "kid-friendly activities near colosseum"
  - "cheap street food in osaka"
  - "best museums in paris"
"""
import logging

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db
from app.core.embeddings import create_enriched_poi_embedding, generate_embeddings
from app.models.poi import POI

logger = logging.getLogger(__name__)
from app.schemas.query import (
    NLQueryRequest,
    NLQueryResponse,
    NLQueryResultItem,
    ParsedIntentResponse,
    RelatedPOIResponse,
    CityInsightResponse,
)
from app.services.query.parser import QueryParser
from app.services.query.searcher import HybridSearcher
from app.services.query.enricher import ResultEnricher

router = APIRouter()

# Parser is stateless — instantiate once
_parser = QueryParser()


@router.post("/search", response_model=NLQueryResponse)
async def natural_language_search(
    request: NLQueryRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Resolve a natural language query against the POI vector database.

    Combines query decomposition, vector similarity, persona scoring,
    and optional knowledge graph enrichment.
    """
    # 1. Parse query into structured intent
    parsed = _parser.parse(request.query)

    # 2. Execute hybrid search
    searcher = HybridSearcher(db)
    results = await searcher.search(parsed=parsed, limit=request.limit)

    # 3. Enrich results with match explanations
    enricher = ResultEnricher(db)
    enriched = await enricher.enrich(
        results=results,
        parsed=parsed,
        include_related=request.include_related,
        include_insights=request.include_insights,
    )

    # 4. Build response
    result_items = []
    for er in enriched:
        poi = er.poi
        item = NLQueryResultItem(
            id=poi.id,
            name=poi.name,
            description=poi.description,
            city=poi.city,
            country=poi.country,
            neighborhood=poi.neighborhood,
            category=poi.category,
            subcategory=poi.subcategory,
            latitude=float(poi.latitude) if poi.latitude else None,
            longitude=float(poi.longitude) if poi.longitude else None,
            cost_level=poi.cost_level,
            avg_cost_per_person=poi.avg_cost_per_person,
            typical_duration_minutes=poi.typical_duration_minutes,
            best_time_of_day=poi.best_time_of_day,
            final_score=er.final_score,
            vector_score=er.vector_score,
            persona_score=er.persona_score,
            match_reasons=er.match_reasons,
            matched_vibes=er.matched_vibes,
            matched_attributes=er.matched_attributes,
            related_pois=(
                [RelatedPOIResponse(**r) for r in er.related_pois]
                if er.related_pois
                else None
            ),
            city_insights=(
                [CityInsightResponse(**i) for i in er.city_insights]
                if er.city_insights
                else None
            ),
        )
        result_items.append(item)

    parsed_intent = ParsedIntentResponse(
        city=parsed.city,
        country=parsed.country,
        category=parsed.category,
        subcategory=parsed.subcategory,
        neighborhood=parsed.neighborhood,
        vibes=parsed.vibes,
        group_type=parsed.group_type,
        attributes=parsed.attributes,
        near_poi_name=parsed.near_poi_name,
        cost_level=parsed.cost_level,
        time_of_day=parsed.time_of_day,
        semantic_query=parsed.semantic_query,
        confidence=parsed.confidence,
    )

    return NLQueryResponse(
        query=request.query,
        parsed_intent=parsed_intent,
        results=result_items,
        total=len(result_items),
    )


@router.post("/re-embed")
async def re_embed_all_pois(
    db: AsyncSession = Depends(get_db),
):
    """
    Re-generate all POI embeddings with enriched text that includes
    persona vibes and attribute tags for better semantic search quality.
    """
    stmt = (
        select(POI)
        .options(
            selectinload(POI.persona_scores),
            selectinload(POI.attributes),
        )
    )
    result = await db.execute(stmt)
    pois = list(result.scalars().all())

    count = 0
    batch_size = 50

    for i in range(0, len(pois), batch_size):
        batch = pois[i : i + batch_size]
        for poi in batch:
            # Build persona scores dict
            ps_dict = None
            if poi.persona_scores:
                ps_dict = {
                    col: getattr(poi.persona_scores, col)
                    for col in dir(poi.persona_scores)
                    if col.startswith("score_")
                }

            # Build attributes dict
            attr_dict = None
            if poi.attributes:
                attr_dict = {
                    "is_hidden_gem": getattr(poi.attributes, "is_hidden_gem", False),
                    "is_must_see": getattr(poi.attributes, "is_must_see", False),
                    "instagram_worthy": getattr(poi.attributes, "instagram_worthy", False),
                    "is_kid_friendly": getattr(poi.attributes, "is_kid_friendly", False),
                }

            embedding = create_enriched_poi_embedding(
                name=poi.name,
                description=poi.description or "",
                category=poi.category or "",
                subcategory=poi.subcategory or "",
                neighborhood=poi.neighborhood or "",
                city=poi.city or "",
                persona_scores=ps_dict,
                attributes=attr_dict,
            )
            poi.description_embedding = embedding
            count += 1

        await db.commit()

    return {"status": "success", "pois_re_embedded": count}
