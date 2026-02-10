from typing import List, Optional
from dataclasses import dataclass
from decimal import Decimal

from app.models.poi import POI, POIPersonaScores
from app.schemas.itinerary import TripRequestCreate
from app.services.rag.retriever import POICandidate
from app.core.config import SCORING_CONFIG


@dataclass
class ScoredPOI:
    """A POI with its final persona match score."""

    poi: POI
    final_score: float
    group_score: float
    vibe_score: float
    similarity_score: float
    selection_reason: str
    is_must_see: bool = False


class PersonaScorer:
    """Scores POIs based on persona matching."""

    # Default weights for scoring components
    DEFAULT_WEIGHTS = {
        "group": 0.30,
        "vibe": 0.30,
        "similarity": 0.15,
        "practical": 0.10,
        "season": 0.15,  # Seasonality weight
    }

    def __init__(self, weights: Optional[dict] = None):
        self.weights = weights or self.DEFAULT_WEIGHTS

    def score_candidates(
        self,
        candidates: List[POICandidate],
        trip_request: TripRequestCreate,
    ) -> List[ScoredPOI]:
        """
        Score all POI candidates based on persona matching.

        Phase 2 of the RAG pipeline: Calculate persona match scores
        for each candidate POI.
        """
        scored_pois = []

        for candidate in candidates:
            scored = self._score_single_poi(
                poi=candidate.poi,
                similarity=candidate.similarity,
                trip_request=trip_request,
            )
            scored_pois.append(scored)

        # Sort by final score (descending)
        scored_pois.sort(key=lambda s: s.final_score, reverse=True)

        return scored_pois

    def _score_single_poi(
        self,
        poi: POI,
        similarity: float,
        trip_request: TripRequestCreate,
    ) -> ScoredPOI:
        """Calculate the persona match score for a single POI."""
        scores = poi.persona_scores

        # Calculate group type score
        group_score = self._get_group_score(scores, trip_request.group_type)

        # Calculate vibe score (average of selected vibes)
        vibe_score = self._get_vibe_score(scores, trip_request.vibes)

        # Calculate practical score based on constraints
        practical_score = self._get_practical_score(poi, trip_request)

        # Calculate season score based on trip dates
        season_score = self._get_season_score(poi, trip_request)

        # Combine scores with weights
        final_score = (
            (group_score * self.weights["group"])
            + (vibe_score * self.weights["vibe"])
            + (similarity * self.weights["similarity"])
            + (practical_score * self.weights["practical"])
            + (season_score * self.weights["season"])
        )

        # Apply must-see boost for iconic attractions
        is_must_see = False
        if poi.attributes and poi.attributes.is_must_see:
            is_must_see = True
            must_see_boost = SCORING_CONFIG.get("must_see_boost", 0.15)
            final_score = min(1.0, final_score + must_see_boost)

        # Generate selection reason
        reason = self._generate_selection_reason(
            poi=poi,
            group_type=trip_request.group_type,
            vibes=trip_request.vibes,
            group_score=group_score,
            vibe_score=vibe_score,
            season=trip_request.trip_season,
            season_score=season_score,
        )

        return ScoredPOI(
            poi=poi,
            final_score=final_score,
            group_score=group_score,
            vibe_score=vibe_score,
            similarity_score=similarity,
            selection_reason=reason,
            is_must_see=is_must_see,
        )

    def _get_group_score(
        self,
        scores: Optional[POIPersonaScores],
        group_type: str,
    ) -> float:
        """Get the score for a specific group type."""
        if not scores:
            return 0.5  # Default neutral score

        score_attr = f"score_{group_type}"
        score = getattr(scores, score_attr, None)

        if score is None:
            return 0.5

        return float(score) if isinstance(score, Decimal) else score

    def _get_vibe_score(
        self,
        scores: Optional[POIPersonaScores],
        vibes: List[str],
    ) -> float:
        """Calculate average score across selected vibes."""
        if not scores or not vibes:
            return 0.5

        vibe_scores = []
        for vibe in vibes:
            score_attr = f"score_{vibe}"
            score = getattr(scores, score_attr, None)
            if score is not None:
                vibe_scores.append(float(score) if isinstance(score, Decimal) else score)

        if not vibe_scores:
            return 0.5

        return sum(vibe_scores) / len(vibe_scores)

    def _get_practical_score(
        self,
        poi: POI,
        trip_request: TripRequestCreate,
    ) -> float:
        """Calculate practical score based on constraints."""
        if not poi.attributes:
            return 0.5

        attrs = poi.attributes
        score = 1.0
        penalties = []

        # Kid-friendliness check
        if trip_request.has_kids and not attrs.is_kid_friendly:
            score -= 0.3
            penalties.append("not kid-friendly")

        # Accessibility check
        if trip_request.mobility_constraints:
            if "wheelchair" in trip_request.mobility_constraints:
                if not attrs.is_wheelchair_accessible:
                    score -= 0.4
                    penalties.append("not wheelchair accessible")

        # Senior-friendliness check (physical intensity)
        if trip_request.has_seniors:
            if attrs.physical_intensity and attrs.physical_intensity > 3:
                score -= 0.2
                penalties.append("too physically demanding for seniors")

        return max(0.0, score)

    def _get_season_score(
        self,
        poi: POI,
        trip_request: TripRequestCreate,
    ) -> float:
        """Calculate season suitability score based on trip dates."""
        scores = poi.persona_scores
        attrs = poi.attributes

        base_score = 0.7  # Default neutral-positive score

        # Get season-specific score if available
        if scores:
            season = trip_request.trip_season
            score_attr = f"score_{season}"
            season_value = getattr(scores, score_attr, None)
            if season_value is not None:
                base_score = float(season_value) if isinstance(season_value, Decimal) else season_value

        # Apply weather-based adjustments
        if attrs:
            # Peak summer heat adjustments
            if trip_request.is_peak_summer:
                if attrs.heat_sensitive:
                    base_score -= 0.2  # Penalize heat-sensitive outdoor spots
                if attrs.is_outdoor and not attrs.is_indoor:
                    base_score -= 0.1  # Slight penalty for outdoor-only in summer
                if attrs.is_indoor:
                    base_score += 0.1  # Boost indoor spots in summer

            # Winter adjustments
            if trip_request.trip_season == "winter":
                if attrs.cold_sensitive:
                    base_score -= 0.15
                if attrs.is_indoor:
                    base_score += 0.1

            # User preferences
            if trip_request.avoid_heat and attrs.heat_sensitive:
                base_score -= 0.15

            if trip_request.prefer_outdoor and attrs.is_outdoor:
                base_score += 0.1
            elif trip_request.prefer_indoor and attrs.is_indoor:
                base_score += 0.1

            # Time of day preferences
            if trip_request.early_riser and attrs.best_in_morning:
                base_score += 0.1
            if trip_request.night_owl and attrs.best_in_evening:
                base_score += 0.1

            # Golden hour bonus for photography vibes
            if "photography" in trip_request.vibes and attrs.sunset_worthy:
                base_score += 0.1

        return max(0.0, min(1.0, base_score))  # Clamp between 0 and 1

    def _generate_selection_reason(
        self,
        poi: POI,
        group_type: str,
        vibes: List[str],
        group_score: float,
        vibe_score: float,
        season: str = None,
        season_score: float = None,
    ) -> str:
        """Generate a human-readable reason for selection."""
        reasons = []

        # Group match
        if group_score >= 0.8:
            reasons.append(f"Excellent match for {group_type} travelers")
        elif group_score >= 0.6:
            reasons.append(f"Good fit for {group_type} groups")

        # Vibe match
        matching_vibes = []
        if poi.persona_scores:
            for vibe in vibes:
                score_attr = f"score_{vibe}"
                score = getattr(poi.persona_scores, score_attr, None)
                if score and float(score) >= 0.7:
                    matching_vibes.append(vibe)

        if matching_vibes:
            reasons.append(f"Strong {', '.join(matching_vibes)} vibes")

        # Season match
        if season and season_score:
            if season_score >= 0.85:
                reasons.append(f"Perfect for {season}")
            elif season_score >= 0.7:
                reasons.append(f"Great choice in {season}")

        # Special attributes
        if poi.attributes:
            if poi.attributes.is_must_see:
                reasons.append("Must-see attraction")
            if poi.attributes.is_hidden_gem:
                reasons.append("Hidden gem")
            if poi.attributes.instagram_worthy:
                reasons.append("Great photo opportunity")
            if poi.attributes.sunset_worthy and "photography" in vibes:
                reasons.append("Stunning at sunset")

        if not reasons:
            reasons.append(f"Matches your {group_type} travel style")

        return "; ".join(reasons)


class POIFilter:
    """Filters POIs based on hard constraints."""

    @staticmethod
    def apply_filters(
        scored_pois: List[ScoredPOI],
        trip_request: TripRequestCreate,
    ) -> List[ScoredPOI]:
        """Apply hard filters to remove incompatible POIs."""
        filtered = []

        for scored in scored_pois:
            if POIFilter._passes_filters(scored.poi, trip_request):
                filtered.append(scored)

        return filtered

    @staticmethod
    def _passes_filters(poi: POI, trip_request: TripRequestCreate) -> bool:
        """Check if a POI passes all hard filters."""
        attrs = poi.attributes

        # If no attributes, assume it passes (be permissive)
        if not attrs:
            return True

        # Hard filter: Must be kid-friendly if traveling with kids
        if trip_request.has_kids:
            # Only filter out if explicitly marked as not kid-friendly
            if attrs.is_kid_friendly is False:
                return False

        # Hard filter: Wheelchair accessibility if required
        if trip_request.mobility_constraints:
            if "wheelchair" in trip_request.mobility_constraints:
                if attrs.is_wheelchair_accessible is False:
                    return False

        # Hard filter: Physical intensity for seniors
        if trip_request.has_seniors:
            if attrs.physical_intensity and attrs.physical_intensity >= 5:
                return False

        # Hard filter: Seasonal closure
        if attrs.seasonal_closure:
            trip_month = trip_request.trip_month
            closure = attrs.seasonal_closure.lower()
            month_names = [
                "january", "february", "march", "april", "may", "june",
                "july", "august", "september", "october", "november", "december"
            ]
            current_month_name = month_names[trip_month - 1]
            if current_month_name in closure:
                return False

        # Hard filter: Outdoor-only during extreme weather (if user specified avoid_heat)
        if trip_request.avoid_heat and trip_request.is_peak_summer:
            if attrs.is_outdoor and not attrs.is_indoor:
                if attrs.heat_sensitive:
                    return False

        return True
