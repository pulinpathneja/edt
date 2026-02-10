"""
First-Level Itinerary Recommendations Service

Provides:
1. Where to Stay - Neighborhood recommendations based on persona
2. What to Visit - Top POIs ranked by persona match and trip duration
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from decimal import Decimal
import json
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.poi import POI, POIPersonaScores


@dataclass
class NeighborhoodRecommendation:
    """A neighborhood recommendation with persona match score."""
    name: str
    description: str
    center_lat: float
    center_lon: float
    match_score: float
    vibes: List[str]
    best_for: List[str]
    reasoning: str


@dataclass
class POIRecommendation:
    """A POI recommendation with persona match details."""
    name: str
    description: str
    category: str
    subcategory: str
    neighborhood: str
    duration_minutes: int
    cost_level: int
    avg_cost: float
    match_score: float
    group_score: float
    vibe_score: float
    priority: str  # "must_see", "highly_recommended", "recommended"
    reasoning: str
    latitude: float
    longitude: float


@dataclass
class FirstLevelItinerary:
    """First-level itinerary overview before detailed planning."""
    city: str
    num_days: int
    group_type: str
    vibes: List[str]
    budget_level: int
    pacing: str

    # Recommendations
    stay_recommendations: List[NeighborhoodRecommendation] = field(default_factory=list)
    poi_recommendations: List[POIRecommendation] = field(default_factory=list)

    # Summary stats
    total_must_see: int = 0
    estimated_daily_cost: float = 0.0
    suggested_pois_per_day: int = 0


class RecommendationService:
    """Service for generating first-level itinerary recommendations."""

    # POIs per day based on pacing
    PACING_POIS = {
        "slow": 3,
        "moderate": 5,
        "fast": 7
    }

    def __init__(self, db: AsyncSession):
        self.db = db
        self._neighborhood_data: Dict[str, List[dict]] = {}
        self._load_neighborhood_data()

    def _load_neighborhood_data(self):
        """Load neighborhood data from seed files."""
        seed_dir = Path(__file__).parent.parent.parent / "data" / "seed"

        for seed_file in seed_dir.glob("*_pois.json"):
            try:
                with open(seed_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    city = data.get("city", seed_file.stem.replace("_pois", "").title())
                    if "neighborhoods" in data:
                        self._neighborhood_data[city] = data["neighborhoods"]
            except Exception:
                pass

    async def generate_first_level_itinerary(
        self,
        city: str,
        num_days: int,
        group_type: str,
        vibes: List[str],
        budget_level: int = 3,
        pacing: str = "moderate",
        has_kids: bool = False,
        has_seniors: bool = False,
    ) -> FirstLevelItinerary:
        """
        Generate a first-level itinerary with stay and visit recommendations.

        Args:
            city: Destination city
            num_days: Number of days for the trip
            group_type: Type of group (family, couple, solo, friends, honeymoon, etc.)
            vibes: List of selected vibes (cultural, foodie, romantic, etc.)
            budget_level: 1-5 budget level
            pacing: slow, moderate, or fast
            has_kids: Whether group has kids
            has_seniors: Whether group has seniors

        Returns:
            FirstLevelItinerary with neighborhood and POI recommendations
        """
        itinerary = FirstLevelItinerary(
            city=city,
            num_days=num_days,
            group_type=group_type,
            vibes=vibes,
            budget_level=budget_level,
            pacing=pacing
        )

        # Get stay recommendations
        itinerary.stay_recommendations = self._get_stay_recommendations(
            city=city,
            group_type=group_type,
            vibes=vibes,
            budget_level=budget_level
        )

        # Get POI recommendations
        pois_needed = self.PACING_POIS.get(pacing, 5) * num_days
        poi_recs = await self._get_poi_recommendations(
            city=city,
            group_type=group_type,
            vibes=vibes,
            budget_level=budget_level,
            limit=pois_needed + 10,  # Get extra for variety
            has_kids=has_kids,
            has_seniors=has_seniors,
        )

        # Prioritize and limit POIs
        itinerary.poi_recommendations = self._prioritize_pois(
            pois=poi_recs,
            num_days=num_days,
            pacing=pacing
        )

        # Calculate summary stats
        itinerary.total_must_see = sum(
            1 for p in itinerary.poi_recommendations if p.priority == "must_see"
        )
        itinerary.suggested_pois_per_day = self.PACING_POIS.get(pacing, 5)

        if itinerary.poi_recommendations:
            daily_pois = itinerary.poi_recommendations[:itinerary.suggested_pois_per_day]
            itinerary.estimated_daily_cost = sum(p.avg_cost for p in daily_pois)

        return itinerary

    def _get_stay_recommendations(
        self,
        city: str,
        group_type: str,
        vibes: List[str],
        budget_level: int,
    ) -> List[NeighborhoodRecommendation]:
        """Get neighborhood stay recommendations based on persona."""
        neighborhoods = self._neighborhood_data.get(city, [])

        if not neighborhoods:
            return []

        recommendations = []

        for nb in neighborhoods:
            # Calculate match score
            score = 0.0
            reasons = []

            # Check if group type matches
            best_for = nb.get("best_for", [])
            if group_type in best_for:
                score += 0.4
                reasons.append(f"Great for {group_type} travelers")
            elif any(g in best_for for g in [group_type, "all"]):
                score += 0.2

            # Check vibe overlap
            nb_vibes = nb.get("vibes", [])
            matching_vibes = set(vibes) & set(nb_vibes)
            if matching_vibes:
                vibe_bonus = len(matching_vibes) / len(vibes) * 0.4
                score += vibe_bonus
                reasons.append(f"Matches your {', '.join(matching_vibes)} vibes")

            # Budget consideration (some neighborhoods are pricier)
            # This is simplified - in production would have actual cost data
            score += 0.2  # Base score

            if score > 0:
                recommendations.append(NeighborhoodRecommendation(
                    name=nb["name"],
                    description=nb.get("description", ""),
                    center_lat=nb.get("center_lat", 0.0),
                    center_lon=nb.get("center_lon", 0.0),
                    match_score=min(score, 1.0),
                    vibes=nb_vibes,
                    best_for=best_for,
                    reasoning="; ".join(reasons) if reasons else "Good central location"
                ))

        # Sort by match score
        recommendations.sort(key=lambda x: x.match_score, reverse=True)

        return recommendations[:5]  # Top 5 neighborhoods

    async def _get_poi_recommendations(
        self,
        city: str,
        group_type: str,
        vibes: List[str],
        budget_level: int,
        limit: int,
        has_kids: bool = False,
        has_seniors: bool = False,
    ) -> List[POIRecommendation]:
        """Get POI recommendations from database based on persona."""

        # Query POIs with persona scores
        stmt = (
            select(POI)
            .options(
                selectinload(POI.persona_scores),
                selectinload(POI.attributes),
            )
            .where(
                POI.city == city,
                (POI.cost_level.is_(None)) | (POI.cost_level <= budget_level + 1),
            )
            .limit(200)  # Get more for scoring
        )

        result = await self.db.execute(stmt)
        pois = result.scalars().all()

        recommendations = []

        for poi in pois:
            scores = poi.persona_scores
            attrs = poi.attributes

            # Skip if doesn't pass hard filters
            if has_kids and attrs and attrs.is_kid_friendly is False:
                continue
            if has_seniors and attrs and attrs.physical_intensity and attrs.physical_intensity >= 5:
                continue

            # Calculate scores
            group_score = self._get_score(scores, f"score_{group_type}")

            vibe_scores = [self._get_score(scores, f"score_{v}") for v in vibes]
            vibe_score = sum(vibe_scores) / len(vibe_scores) if vibe_scores else 0.5

            # Combined score
            match_score = (group_score * 0.4) + (vibe_score * 0.4) + 0.2

            # Determine priority
            priority = "recommended"
            if attrs and attrs.is_must_see:
                priority = "must_see"
                match_score += 0.1
            elif match_score >= 0.75:
                priority = "highly_recommended"

            # Generate reasoning
            reasoning = self._generate_poi_reasoning(
                poi=poi,
                group_type=group_type,
                vibes=vibes,
                group_score=group_score,
                vibe_score=vibe_score
            )

            recommendations.append(POIRecommendation(
                name=poi.name,
                description=poi.description or "",
                category=poi.category or "attraction",
                subcategory=poi.subcategory or "",
                neighborhood=poi.neighborhood or "",
                duration_minutes=poi.typical_duration_minutes or 60,
                cost_level=poi.cost_level or 2,
                avg_cost=float(poi.avg_cost_per_person) if poi.avg_cost_per_person else 0.0,
                match_score=min(match_score, 1.0),
                group_score=group_score,
                vibe_score=vibe_score,
                priority=priority,
                reasoning=reasoning,
                latitude=poi.latitude or 0.0,
                longitude=poi.longitude or 0.0,
            ))

        # Sort by match score
        recommendations.sort(key=lambda x: (x.priority == "must_see", x.match_score), reverse=True)

        return recommendations[:limit]

    def _prioritize_pois(
        self,
        pois: List[POIRecommendation],
        num_days: int,
        pacing: str,
    ) -> List[POIRecommendation]:
        """Prioritize and limit POIs based on trip duration and pacing."""
        pois_per_day = self.PACING_POIS.get(pacing, 5)
        total_pois = pois_per_day * num_days

        # Ensure we have variety - mix categories
        selected = []
        must_sees = [p for p in pois if p.priority == "must_see"]
        others = [p for p in pois if p.priority != "must_see"]

        # Add all must-sees first (up to 60% of total)
        max_must_sees = int(total_pois * 0.6)
        selected.extend(must_sees[:max_must_sees])

        # Fill rest with highly recommended and recommended
        remaining = total_pois - len(selected)
        selected.extend(others[:remaining])

        return selected

    def _get_score(self, scores: Optional[POIPersonaScores], attr: str) -> float:
        """Safely get a score attribute."""
        if not scores:
            return 0.5
        score = getattr(scores, attr, None)
        if score is None:
            return 0.5
        return float(score) if isinstance(score, Decimal) else score

    def _generate_poi_reasoning(
        self,
        poi: POI,
        group_type: str,
        vibes: List[str],
        group_score: float,
        vibe_score: float,
    ) -> str:
        """Generate human-readable reasoning for POI selection."""
        reasons = []

        if group_score >= 0.8:
            reasons.append(f"Excellent for {group_type} travelers")
        elif group_score >= 0.6:
            reasons.append(f"Good fit for {group_type} groups")

        # Check which vibes match well
        scores = poi.persona_scores
        if scores:
            matching_vibes = []
            for vibe in vibes:
                score = self._get_score(scores, f"score_{vibe}")
                if score >= 0.7:
                    matching_vibes.append(vibe)
            if matching_vibes:
                reasons.append(f"Strong {', '.join(matching_vibes)} vibes")

        # Add attribute-based reasons
        attrs = poi.attributes
        if attrs:
            if attrs.is_must_see:
                reasons.append("Iconic must-see attraction")
            if attrs.is_hidden_gem:
                reasons.append("Local hidden gem")
            if attrs.instagram_worthy:
                reasons.append("Great for photos")
            if attrs.sunset_worthy and "photography" in vibes:
                reasons.append("Beautiful at sunset")

        if not reasons:
            reasons.append(f"Matches your {group_type} travel style")

        return "; ".join(reasons)


# Convenience function for API use
async def get_first_level_recommendations(
    db: AsyncSession,
    city: str,
    num_days: int,
    group_type: str,
    vibes: List[str],
    budget_level: int = 3,
    pacing: str = "moderate",
    has_kids: bool = False,
    has_seniors: bool = False,
) -> FirstLevelItinerary:
    """Get first-level itinerary recommendations."""
    service = RecommendationService(db)
    return await service.generate_first_level_itinerary(
        city=city,
        num_days=num_days,
        group_type=group_type,
        vibes=vibes,
        budget_level=budget_level,
        pacing=pacing,
        has_kids=has_kids,
        has_seniors=has_seniors,
    )
