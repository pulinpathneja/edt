"""
Result enricher that adds match explanations, knowledge graph
related POIs, and city insights to search results.
"""
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.poi import POI
from app.models.city_insight import CityInsight
from app.services.query.parser import ParsedQuery
from app.services.query.searcher import SearchResult

logger = logging.getLogger(__name__)


@dataclass
class EnrichedResult:
    """A search result with explanations and optional enrichments."""

    poi: POI
    final_score: float
    vector_score: float
    persona_score: float
    attribute_score: float
    proximity_score: float
    match_reasons: List[str] = field(default_factory=list)
    matched_vibes: List[str] = field(default_factory=list)
    matched_attributes: List[str] = field(default_factory=list)
    related_pois: Optional[List[Dict[str, Any]]] = None
    city_insights: Optional[List[Dict[str, Any]]] = None


class ResultEnricher:
    """Enriches search results with explanations and related context."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def enrich(
        self,
        results: List[SearchResult],
        parsed: ParsedQuery,
        include_related: bool = False,
        include_insights: bool = False,
    ) -> List[EnrichedResult]:
        """Enrich a list of search results."""
        enriched = []
        for sr in results:
            reasons = self._generate_match_reasons(sr.poi, parsed, sr)
            matched_vibes = self._get_matched_vibes(sr.poi, parsed)
            matched_attrs = self._get_matched_attributes(sr.poi, parsed)

            er = EnrichedResult(
                poi=sr.poi,
                final_score=sr.final_score,
                vector_score=sr.vector_score,
                persona_score=sr.persona_score,
                attribute_score=sr.attribute_score,
                proximity_score=sr.proximity_score,
                match_reasons=reasons,
                matched_vibes=matched_vibes,
                matched_attributes=matched_attrs,
            )

            if include_related:
                er.related_pois = await self._fetch_related_pois(sr.poi.id)

            enriched.append(er)

        if include_insights and parsed.city:
            insights = await self._fetch_city_insights(parsed.city)
            if insights and enriched:
                # Attach insights to the first result as a summary
                enriched[0].city_insights = insights

        return enriched

    def _generate_match_reasons(
        self, poi: POI, parsed: ParsedQuery, sr: SearchResult
    ) -> List[str]:
        """Generate human-readable match reasons."""
        reasons = []

        # Vibe matches with scores
        if poi.persona_scores and parsed.vibes:
            for vibe in parsed.vibes:
                score_attr = f"score_{vibe}"
                value = getattr(poi.persona_scores, score_attr, None)
                if value is not None:
                    val = float(value)
                    if val >= 0.8:
                        reasons.append(f"Excellent {vibe} match ({val:.0%})")
                    elif val >= 0.6:
                        reasons.append(f"Good {vibe} match ({val:.0%})")

        # Group type match
        if poi.persona_scores and parsed.group_type:
            score_attr = f"score_{parsed.group_type}"
            value = getattr(poi.persona_scores, score_attr, None)
            if value is not None and float(value) >= 0.7:
                reasons.append(f"Great for {parsed.group_type}")

        # Attribute matches
        if poi.attributes:
            if (
                getattr(poi.attributes, "is_hidden_gem", False)
                and "is_hidden_gem" in parsed.attributes
            ):
                reasons.append("Hidden gem")
            if getattr(poi.attributes, "is_must_see", False):
                reasons.append("Must-see attraction")
            if (
                getattr(poi.attributes, "instagram_worthy", False)
                and "instagram_worthy" in parsed.attributes
            ):
                reasons.append("Great photo opportunity")
            if (
                getattr(poi.attributes, "is_kid_friendly", False)
                and "is_kid_friendly" in parsed.attributes
            ):
                reasons.append("Kid-friendly")

        # Category match
        if parsed.category and poi.category == parsed.category:
            reasons.append(f"Matches {parsed.category} search")

        # Neighborhood
        if poi.neighborhood:
            reasons.append(f"In {poi.neighborhood}")

        # Proximity
        if parsed.near_poi_name and sr.proximity_score >= 0.8:
            reasons.append(f"Close to {parsed.near_poi_name}")

        # Fallback
        if not reasons:
            reasons.append("Semantically similar to your search")

        return reasons

    @staticmethod
    def _get_matched_vibes(poi: POI, parsed: ParsedQuery) -> List[str]:
        """Return vibes where the POI scores well."""
        matched = []
        if not poi.persona_scores:
            return matched
        for vibe in parsed.vibes:
            score_attr = f"score_{vibe}"
            value = getattr(poi.persona_scores, score_attr, None)
            if value is not None and float(value) >= 0.6:
                matched.append(vibe)
        return matched

    @staticmethod
    def _get_matched_attributes(poi: POI, parsed: ParsedQuery) -> List[str]:
        """Return attribute flags that match the query."""
        matched = []
        if not poi.attributes:
            return matched
        for attr_key in parsed.attributes:
            value = getattr(poi.attributes, attr_key, None)
            if value is True:
                matched.append(attr_key)
        return matched

    async def _fetch_related_pois(
        self, poi_id: UUID, limit: int = 3
    ) -> List[Dict[str, Any]]:
        """Fetch related POIs from the knowledge graph."""
        try:
            from app.services.knowledge_graph import (
                KnowledgeGraphService,
                RelationshipType,
            )

            kg = KnowledgeGraphService(self.db)
            related = await kg.get_related_pois(
                poi_id,
                relationship_types=[
                    RelationshipType.PAIRS_WELL_WITH,
                    RelationshipType.NEAR_TO,
                    RelationshipType.SAME_THEME,
                ],
                limit=limit,
            )
            return [
                {
                    "id": str(r["poi"].id),
                    "name": r["poi"].name,
                    "category": r["poi"].category,
                    "relationship_type": r["relationship_type"],
                    "strength": r.get("strength"),
                    "distance_meters": r.get("distance_meters"),
                }
                for r in related
            ]
        except Exception as e:
            logger.warning(f"Knowledge graph lookup failed: {e}")
            return []

    async def _fetch_city_insights(
        self, city: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Fetch relevant city insights from the database."""
        try:
            city_slug = city.lower().replace(" ", "_")
            stmt = (
                select(CityInsight)
                .where(CityInsight.city == city_slug)
                .order_by(CityInsight.relevance_score.desc())
                .limit(limit)
            )
            result = await self.db.execute(stmt)
            rows = result.scalars().all()
            return [
                {
                    "title": row.title,
                    "source": row.source,
                    "category": row.category,
                    "content": (row.content or "")[:300],
                    "url": row.url,
                }
                for row in rows
            ]
        except Exception as e:
            logger.warning(f"City insights lookup failed: {e}")
            return []
