"""
Hybrid searcher that combines vector similarity, SQL filters,
persona score boosting, attribute matching, and proximity resolution.
"""
import math
from dataclasses import dataclass
from typing import List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.embeddings import generate_embedding
from app.models.poi import POI, POIAttributes, POIPersonaScores
from app.services.query.parser import ParsedQuery


@dataclass
class SearchResult:
    """A single search result with scoring breakdown."""

    poi: POI
    final_score: float
    vector_score: float
    persona_score: float
    attribute_score: float
    proximity_score: float


class HybridSearcher:
    """Executes hybrid vector + structured search over POIs."""

    # Default scoring weights
    VECTOR_WEIGHT = 0.40
    PERSONA_WEIGHT = 0.35
    ATTRIBUTE_WEIGHT = 0.15
    PROXIMITY_WEIGHT = 0.10

    def __init__(self, db: AsyncSession):
        self.db = db

    async def search(
        self,
        parsed: ParsedQuery,
        limit: int = 20,
    ) -> List[SearchResult]:
        """
        Execute hybrid search:
        1. Vector similarity on semantic_query (or full query)
        2. SQL filters on city, category, subcategory, cost_level
        3. Persona score boosting on extracted vibes and group_type
        4. Attribute matching bonus
        5. Proximity re-ranking if spatial modifier detected
        """
        # Determine embedding text: use semantic_query if available, else raw query
        embedding_text = parsed.semantic_query.strip() or parsed.raw_query
        query_embedding = generate_embedding(embedding_text)

        # Build filtered vector query
        stmt = (
            select(
                POI,
                (1 - POI.description_embedding.cosine_distance(query_embedding)).label(
                    "vector_score"
                ),
            )
            .options(
                selectinload(POI.persona_scores),
                selectinload(POI.attributes),
            )
            .where(POI.description_embedding.isnot(None))
        )

        # Apply hard filters
        stmt = self._apply_filters(stmt, parsed)

        # Over-fetch for re-ranking
        fetch_limit = limit * 3
        stmt = stmt.order_by(
            POI.description_embedding.cosine_distance(query_embedding)
        )
        stmt = stmt.limit(fetch_limit)

        result = await self.db.execute(stmt)
        rows = result.all()

        # If too few results, try with relaxed filters
        if len(rows) < 3 and self._has_restrictive_filters(parsed):
            rows = await self._fallback_search(
                query_embedding, parsed, fetch_limit, rows
            )

        # Resolve proximity anchor if needed
        anchor_coords: Optional[Tuple[float, float]] = None
        if parsed.near_poi_name:
            anchor_coords = await self._resolve_poi_location(parsed.near_poi_name)

        # Re-rank with composite scoring
        results = []
        for poi, vector_score in rows:
            vs = float(vector_score) if vector_score else 0.0
            ps = self._compute_persona_boost(poi, parsed)
            attr_s = self._compute_attribute_boost(poi, parsed)
            prox_s = self._compute_proximity_score(poi, anchor_coords)

            final = (
                vs * self.VECTOR_WEIGHT
                + ps * self.PERSONA_WEIGHT
                + attr_s * self.ATTRIBUTE_WEIGHT
                + prox_s * self.PROXIMITY_WEIGHT
            )

            results.append(
                SearchResult(
                    poi=poi,
                    final_score=round(final, 4),
                    vector_score=round(vs, 4),
                    persona_score=round(ps, 4),
                    attribute_score=round(attr_s, 4),
                    proximity_score=round(prox_s, 4),
                )
            )

        # Sort by final score
        results.sort(key=lambda r: r.final_score, reverse=True)
        return results[:limit]

    def _apply_filters(self, stmt, parsed: ParsedQuery):
        """Apply SQL WHERE clauses from parsed query."""
        if parsed.city:
            stmt = stmt.where(POI.city.ilike(f"%{parsed.city}%"))
        if parsed.category:
            stmt = stmt.where(POI.category == parsed.category)
        if parsed.subcategory:
            stmt = stmt.where(POI.subcategory == parsed.subcategory)
        if parsed.cost_level:
            stmt = stmt.where(
                (POI.cost_level.is_(None)) | (POI.cost_level <= parsed.cost_level)
            )
        if parsed.time_of_day:
            stmt = stmt.where(
                (POI.best_time_of_day.is_(None))
                | (POI.best_time_of_day.in_([parsed.time_of_day, "any"]))
            )
        if parsed.neighborhood:
            stmt = stmt.where(POI.neighborhood.ilike(f"%{parsed.neighborhood}%"))
        return stmt

    @staticmethod
    def _has_restrictive_filters(parsed: ParsedQuery) -> bool:
        """Check if the parsed query has filters that could be too restrictive."""
        filter_count = sum(
            [
                bool(parsed.category),
                bool(parsed.subcategory),
                bool(parsed.cost_level),
                bool(parsed.time_of_day),
                bool(parsed.neighborhood),
            ]
        )
        return filter_count >= 2

    async def _fallback_search(
        self,
        query_embedding,
        parsed: ParsedQuery,
        fetch_limit: int,
        existing_rows: list,
    ) -> list:
        """Progressively relax filters to get more results."""
        # Try dropping subcategory first
        relaxed = ParsedQuery(
            raw_query=parsed.raw_query,
            city=parsed.city,
            category=parsed.category,
            vibes=parsed.vibes,
            group_type=parsed.group_type,
            attributes=parsed.attributes,
        )

        stmt = (
            select(
                POI,
                (1 - POI.description_embedding.cosine_distance(query_embedding)).label(
                    "vector_score"
                ),
            )
            .options(
                selectinload(POI.persona_scores),
                selectinload(POI.attributes),
            )
            .where(POI.description_embedding.isnot(None))
        )
        stmt = self._apply_filters(stmt, relaxed)
        stmt = stmt.order_by(
            POI.description_embedding.cosine_distance(query_embedding)
        )
        stmt = stmt.limit(fetch_limit)

        result = await self.db.execute(stmt)
        rows = result.all()

        if len(rows) >= 3:
            return rows

        # Further relax: city-only
        if parsed.city:
            stmt = (
                select(
                    POI,
                    (
                        1 - POI.description_embedding.cosine_distance(query_embedding)
                    ).label("vector_score"),
                )
                .options(
                    selectinload(POI.persona_scores),
                    selectinload(POI.attributes),
                )
                .where(POI.description_embedding.isnot(None))
                .where(POI.city.ilike(f"%{parsed.city}%"))
                .order_by(POI.description_embedding.cosine_distance(query_embedding))
                .limit(fetch_limit)
            )
            result = await self.db.execute(stmt)
            rows = result.all()

        return rows if rows else existing_rows

    @staticmethod
    def _compute_persona_boost(poi: POI, parsed: ParsedQuery) -> float:
        """Compute persona-based boost from extracted vibes and group type."""
        scores = poi.persona_scores
        if not scores:
            return 0.5

        components = []

        for vibe in parsed.vibes:
            score_attr = f"score_{vibe}"
            value = getattr(scores, score_attr, None)
            if value is not None:
                components.append(float(value))

        if parsed.group_type:
            score_attr = f"score_{parsed.group_type}"
            value = getattr(scores, score_attr, None)
            if value is not None:
                components.append(float(value))

        if components:
            return sum(components) / len(components)
        return 0.5

    @staticmethod
    def _compute_attribute_boost(poi: POI, parsed: ParsedQuery) -> float:
        """Compute bonus for matching attribute flags."""
        attrs = poi.attributes
        if not attrs or not parsed.attributes:
            return 0.5

        matches = 0
        for attr_key in parsed.attributes:
            value = getattr(attrs, attr_key, None)
            if value is True:
                matches += 1

        return 0.5 + (0.5 * matches / len(parsed.attributes))

    @staticmethod
    def _compute_proximity_score(
        poi: POI, anchor_coords: Optional[Tuple[float, float]]
    ) -> float:
        """Compute proximity score based on distance to anchor point."""
        if not anchor_coords:
            return 0.5  # neutral

        if not poi.latitude or not poi.longitude:
            return 0.3

        distance_km = _haversine(
            float(poi.latitude),
            float(poi.longitude),
            anchor_coords[0],
            anchor_coords[1],
        )

        # Score: 1.0 for 0km, decays to 0.0 at 5km+
        if distance_km <= 0.5:
            return 1.0
        elif distance_km <= 1.0:
            return 0.8
        elif distance_km <= 2.0:
            return 0.6
        elif distance_km <= 5.0:
            return 0.3
        return 0.1

    async def _resolve_poi_location(
        self, poi_name: str
    ) -> Optional[Tuple[float, float]]:
        """Resolve a POI name to lat/lon coordinates."""
        stmt = (
            select(POI.latitude, POI.longitude)
            .where(POI.name.ilike(f"%{poi_name}%"))
            .where(POI.latitude.isnot(None))
            .where(POI.longitude.isnot(None))
            .limit(1)
        )
        result = await self.db.execute(stmt)
        row = result.first()
        if row and row.latitude and row.longitude:
            return (float(row.latitude), float(row.longitude))
        return None


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in km between two lat/lon points."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c
