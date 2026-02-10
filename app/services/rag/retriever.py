from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from sqlalchemy.orm import selectinload

from app.models.poi import POI, POIPersonaScores, POIAttributes
from app.core.embeddings import create_poi_query_embedding
from app.schemas.itinerary import TripRequestCreate


class POICandidate:
    """A POI candidate with similarity score."""

    def __init__(self, poi: POI, similarity: float):
        self.poi = poi
        self.similarity = similarity


class POIRetriever:
    """Retrieves POI candidates using vector similarity search."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def retrieve_candidates(
        self,
        trip_request: TripRequestCreate,
        limit: int = 100,
        exclude_poi_ids: Optional[List[UUID]] = None,
    ) -> List[POICandidate]:
        """
        Retrieve POI candidates using semantic search.

        Phase 1 of the RAG pipeline: Find POIs that semantically match
        the user's trip preferences.
        """
        # Create query embedding from user preferences
        query_embedding = create_poi_query_embedding(
            destination=trip_request.destination_city,
            group_type=trip_request.group_type,
            vibes=trip_request.vibes,
            pacing=trip_request.pacing,
        )

        # Build exclusion clause
        exclude_clause = ""
        params = {
            "embedding": str(query_embedding),
            "budget_level": trip_request.budget_level,
            "city": trip_request.destination_city,
            "limit": limit,
        }

        if exclude_poi_ids:
            exclude_clause = "AND p.id NOT IN :exclude_ids"
            params["exclude_ids"] = tuple(str(id) for id in exclude_poi_ids)

        # Vector similarity search with cost and city filter
        query = text(f"""
            SELECT
                p.id,
                p.name,
                p.description,
                p.latitude,
                p.longitude,
                p.address,
                p.neighborhood,
                p.city,
                p.country,
                p.category,
                p.subcategory,
                p.typical_duration_minutes,
                p.best_time_of_day,
                p.best_days,
                p.seasonal_availability,
                p.cost_level,
                p.avg_cost_per_person,
                p.cost_currency,
                p.source,
                p.source_id,
                p.created_at,
                p.updated_at,
                1 - (p.description_embedding <=> :embedding::vector) as similarity
            FROM pois p
            WHERE p.city = :city
                AND (p.cost_level IS NULL OR p.cost_level <= :budget_level)
                AND p.description_embedding IS NOT NULL
                {exclude_clause}
            ORDER BY p.description_embedding <=> :embedding::vector
            LIMIT :limit
        """)

        result = await self.db.execute(query, params)
        rows = result.fetchall()

        # Fetch full POI objects with relationships
        poi_ids = [row.id for row in rows]
        similarity_map = {row.id: row.similarity for row in rows}

        if not poi_ids:
            return []

        # Get POIs with their persona scores and attributes
        stmt = (
            select(POI)
            .options(
                selectinload(POI.persona_scores),
                selectinload(POI.attributes),
            )
            .where(POI.id.in_(poi_ids))
        )
        pois_result = await self.db.execute(stmt)
        pois = pois_result.scalars().all()

        # Create candidates with similarity scores
        candidates = []
        for poi in pois:
            similarity = similarity_map.get(poi.id, 0.0)
            candidates.append(POICandidate(poi=poi, similarity=float(similarity)))

        # Sort by similarity (descending)
        candidates.sort(key=lambda c: c.similarity, reverse=True)

        return candidates

    async def retrieve_by_category(
        self,
        city: str,
        category: str,
        budget_level: int,
        limit: int = 20,
        exclude_poi_ids: Optional[List[UUID]] = None,
    ) -> List[POI]:
        """Retrieve POIs by category for specific slot filling."""
        stmt = (
            select(POI)
            .options(
                selectinload(POI.persona_scores),
                selectinload(POI.attributes),
            )
            .where(
                POI.city == city,
                POI.category == category,
                (POI.cost_level.is_(None)) | (POI.cost_level <= budget_level),
            )
        )

        if exclude_poi_ids:
            stmt = stmt.where(POI.id.notin_(exclude_poi_ids))

        stmt = stmt.limit(limit)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def retrieve_nearby(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 1.0,
        budget_level: int = 5,
        limit: int = 20,
        exclude_poi_ids: Optional[List[UUID]] = None,
    ) -> List[POI]:
        """Retrieve POIs within a certain radius for proximity-based scheduling."""
        # Using Haversine formula approximation for distance
        params = {
            "lat": latitude,
            "lng": longitude,
            "radius": radius_km,
            "budget_level": budget_level,
            "limit": limit,
        }

        exclude_clause = ""
        if exclude_poi_ids:
            exclude_clause = "AND id NOT IN :exclude_ids"
            params["exclude_ids"] = tuple(str(id) for id in exclude_poi_ids)

        query = text(f"""
            SELECT *,
                (6371 * acos(cos(radians(:lat))
                    * cos(radians(latitude))
                    * cos(radians(longitude) - radians(:lng))
                    + sin(radians(:lat))
                    * sin(radians(latitude)))) AS distance_km
            FROM pois
            WHERE latitude IS NOT NULL
                AND longitude IS NOT NULL
                AND (cost_level IS NULL OR cost_level <= :budget_level)
                {exclude_clause}
            HAVING distance_km <= :radius
            ORDER BY distance_km
            LIMIT :limit
        """)

        result = await self.db.execute(query, params)
        rows = result.fetchall()

        poi_ids = [row.id for row in rows]
        if not poi_ids:
            return []

        stmt = (
            select(POI)
            .options(
                selectinload(POI.persona_scores),
                selectinload(POI.attributes),
            )
            .where(POI.id.in_(poi_ids))
        )
        pois_result = await self.db.execute(stmt)
        return list(pois_result.scalars().all())
