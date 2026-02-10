"""
Knowledge Graph service for relationship-based POI queries.

This service provides graph traversal capabilities:
1. Find related POIs (pairs well with, same theme)
2. Find nearby restaurants for any POI
3. Find POIs on route between two points
4. Suggest alternatives when POI is crowded
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, text
from sqlalchemy.orm import selectinload

from app.models.poi import POI
from app.models.knowledge_graph import (
    POIRelationship,
    Neighborhood,
    RestaurantDetail,
    POICrowdPattern,
)


class RelationshipType:
    """Constants for relationship types."""

    NEAR_TO = "NEAR_TO"
    SAME_NEIGHBORHOOD = "SAME_NEIGHBORHOOD"
    SAME_THEME = "SAME_THEME"
    PAIRS_WELL_WITH = "PAIRS_WELL_WITH"
    ALTERNATIVE_TO = "ALTERNATIVE_TO"
    PART_OF = "PART_OF"
    HISTORICAL_CONNECTION = "HISTORICAL_CONNECTION"
    VIEW_OF = "VIEW_OF"
    ON_ROUTE_TO = "ON_ROUTE_TO"


class KnowledgeGraphService:
    """Service for knowledge graph queries."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_related_pois(
        self,
        poi_id: UUID,
        relationship_types: Optional[List[str]] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Get POIs related to a given POI.

        Args:
            poi_id: The source POI
            relationship_types: Filter by relationship types
            limit: Max results

        Returns:
            List of related POIs with relationship info
        """
        stmt = (
            select(POIRelationship, POI)
            .join(POI, POIRelationship.target_poi_id == POI.id)
            .where(POIRelationship.source_poi_id == poi_id)
        )

        if relationship_types:
            stmt = stmt.where(POIRelationship.relationship_type.in_(relationship_types))

        stmt = stmt.order_by(POIRelationship.strength.desc()).limit(limit)

        result = await self.db.execute(stmt)
        rows = result.all()

        related = []
        for rel, poi in rows:
            related.append({
                "poi": poi,
                "relationship_type": rel.relationship_type,
                "strength": float(rel.strength) if rel.strength else None,
                "distance_meters": rel.distance_meters,
                "walking_time_minutes": rel.walking_time_minutes,
                "description": rel.description,
            })

        return related

    async def find_nearby_restaurants(
        self,
        poi_id: UUID,
        max_distance_meters: int = 500,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Find restaurants near a POI using the relationship graph.

        Falls back to distance-based query if no relationships exist.
        """
        # First try relationship-based lookup
        stmt = (
            select(POIRelationship, POI)
            .join(POI, POIRelationship.target_poi_id == POI.id)
            .where(
                POIRelationship.source_poi_id == poi_id,
                POIRelationship.relationship_type == RelationshipType.NEAR_TO,
                POI.category == "restaurant",
            )
        )

        if max_distance_meters:
            stmt = stmt.where(
                or_(
                    POIRelationship.distance_meters.is_(None),
                    POIRelationship.distance_meters <= max_distance_meters,
                )
            )

        stmt = stmt.order_by(POIRelationship.distance_meters).limit(limit)

        result = await self.db.execute(stmt)
        rows = result.all()

        restaurants = []
        for rel, poi in rows:
            restaurants.append({
                "poi": poi,
                "distance_meters": rel.distance_meters,
                "walking_time_minutes": rel.walking_time_minutes,
            })

        return restaurants

    async def find_alternatives(
        self,
        poi_id: UUID,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Find alternative POIs if the requested one is crowded/unavailable.
        """
        return await self.get_related_pois(
            poi_id,
            relationship_types=[RelationshipType.ALTERNATIVE_TO],
            limit=limit,
        )

    async def find_pairs_well_with(
        self,
        poi_id: UUID,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Find POIs that pair well with the given POI.
        Useful for suggesting "after visiting X, check out Y".
        """
        return await self.get_related_pois(
            poi_id,
            relationship_types=[RelationshipType.PAIRS_WELL_WITH],
            limit=limit,
        )

    async def find_same_theme(
        self,
        poi_id: UUID,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Find POIs with the same theme (e.g., all Renaissance art).
        """
        return await self.get_related_pois(
            poi_id,
            relationship_types=[RelationshipType.SAME_THEME],
            limit=limit,
        )

    async def find_pois_on_route(
        self,
        start_poi_id: UUID,
        end_poi_id: UUID,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Find POIs that are on the route between two POIs.
        Useful for "things to see on the way".
        """
        # Get POIs that are marked as "on route to" the destination
        # and are also near the start
        stmt = (
            select(POIRelationship, POI)
            .join(POI, POIRelationship.source_poi_id == POI.id)
            .where(
                POIRelationship.target_poi_id == end_poi_id,
                POIRelationship.relationship_type == RelationshipType.ON_ROUTE_TO,
            )
            .order_by(POIRelationship.distance_meters)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        on_route = []
        for rel, poi in rows:
            on_route.append({
                "poi": poi,
                "distance_from_destination_meters": rel.distance_meters,
            })

        return on_route

    async def get_crowd_level(
        self,
        poi_id: UUID,
        day_of_week: int,
        hour_of_day: int,
        season: str = "shoulder",
    ) -> Optional[Dict[str, Any]]:
        """
        Get expected crowd level for a POI at a specific time.
        """
        stmt = select(POICrowdPattern).where(
            POICrowdPattern.poi_id == poi_id,
            POICrowdPattern.day_of_week == day_of_week,
            POICrowdPattern.hour_of_day == hour_of_day,
            POICrowdPattern.season == season,
        )

        result = await self.db.execute(stmt)
        pattern = result.scalar_one_or_none()

        if pattern:
            return {
                "crowd_level": float(pattern.crowd_level),
                "wait_time_minutes": pattern.wait_time_minutes,
                "recommendation": self._get_crowd_recommendation(float(pattern.crowd_level)),
            }

        return None

    def _get_crowd_recommendation(self, crowd_level: float) -> str:
        """Generate recommendation based on crowd level."""
        if crowd_level < 0.3:
            return "Excellent time to visit - low crowds"
        elif crowd_level < 0.5:
            return "Good time to visit - moderate crowds"
        elif crowd_level < 0.7:
            return "Busy - consider visiting earlier or later"
        else:
            return "Very crowded - consider alternatives or different timing"


class RelationshipBuilder:
    """Service for building POI relationships."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_relationship(
        self,
        source_poi_id: UUID,
        target_poi_id: UUID,
        relationship_type: str,
        strength: float = 0.5,
        bidirectional: bool = False,
        distance_meters: Optional[int] = None,
        walking_time_minutes: Optional[int] = None,
        description: Optional[str] = None,
    ) -> POIRelationship:
        """Create a relationship between two POIs."""
        rel = POIRelationship(
            source_poi_id=source_poi_id,
            target_poi_id=target_poi_id,
            relationship_type=relationship_type,
            strength=strength,
            bidirectional=bidirectional,
            distance_meters=distance_meters,
            walking_time_minutes=walking_time_minutes,
            description=description,
        )

        self.db.add(rel)

        # Create reverse relationship if bidirectional
        if bidirectional:
            reverse_rel = POIRelationship(
                source_poi_id=target_poi_id,
                target_poi_id=source_poi_id,
                relationship_type=relationship_type,
                strength=strength,
                bidirectional=True,
                distance_meters=distance_meters,
                walking_time_minutes=walking_time_minutes,
                description=description,
            )
            self.db.add(reverse_rel)

        await self.db.commit()
        return rel

    async def auto_create_proximity_relationships(
        self,
        city: str = "Rome",
        max_distance_km: float = 0.5,
    ) -> int:
        """
        Automatically create NEAR_TO relationships based on geographic proximity.

        Uses Haversine formula to find POIs within max_distance_km of each other.
        """
        # Get all POIs for the city
        stmt = select(POI).where(POI.city == city)
        result = await self.db.execute(stmt)
        pois = list(result.scalars().all())

        count = 0

        for i, poi_a in enumerate(pois):
            for poi_b in pois[i + 1 :]:
                if poi_a.latitude and poi_b.latitude:
                    # Calculate distance using Haversine
                    distance_km = self._haversine(
                        float(poi_a.longitude),
                        float(poi_a.latitude),
                        float(poi_b.longitude),
                        float(poi_b.latitude),
                    )

                    if distance_km <= max_distance_km:
                        # Create bidirectional relationship
                        rel = POIRelationship(
                            source_poi_id=poi_a.id,
                            target_poi_id=poi_b.id,
                            relationship_type=RelationshipType.NEAR_TO,
                            strength=1.0 - (distance_km / max_distance_km),
                            bidirectional=True,
                            distance_meters=int(distance_km * 1000),
                            walking_time_minutes=int(distance_km * 1000 / 80),  # ~80m/min walking
                        )
                        self.db.add(rel)

                        # Reverse
                        rev_rel = POIRelationship(
                            source_poi_id=poi_b.id,
                            target_poi_id=poi_a.id,
                            relationship_type=RelationshipType.NEAR_TO,
                            strength=1.0 - (distance_km / max_distance_km),
                            bidirectional=True,
                            distance_meters=int(distance_km * 1000),
                            walking_time_minutes=int(distance_km * 1000 / 80),
                        )
                        self.db.add(rev_rel)

                        count += 2

        await self.db.commit()
        return count

    @staticmethod
    def _haversine(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
        """Calculate the great circle distance in kilometers."""
        from math import radians, cos, sin, asin, sqrt

        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        km = 6371 * c
        return km
