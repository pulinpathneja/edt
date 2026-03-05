from typing import List, Optional

from app.schemas.landmark import (
    LandmarkEnhanced,
    LandmarkVibeScores,
    LandmarkGroupScores,
    MustSeeRating,
)


class LandmarkScorer:
    """Scores landmarks with must-see prioritization.

    Priority order:
    1. Must-see tier (iconic landmarks always win)
    2. Vibe compatibility
    3. Group compatibility
    """

    MUST_SEE_BOOSTS = {
        "iconic": 0.35,
        "recommended": 0.20,
        "optional": 0.05,
    }

    SCORE_FLOORS = {
        "iconic": 0.75,
        "recommended": 0.50,
        "optional": 0.0,
    }

    def score_landmark(
        self,
        landmark: LandmarkEnhanced,
        vibes: List[str],
        group_type: str,
    ) -> float:
        """Calculate final score with must-see prioritization."""
        vibe_score = self._calculate_vibe_score(landmark.vibe_scores, vibes)
        group_score = getattr(landmark.group_scores, group_type, 0.5)

        base_score = (vibe_score * 0.5) + (group_score * 0.5)

        if landmark.must_see_rating.is_must_see:
            tier = landmark.must_see_rating.tier
            boost = self.MUST_SEE_BOOSTS.get(tier, 0)
            floor = self.SCORE_FLOORS.get(tier, 0)
            final_score = max(floor, base_score + boost)
            final_score = min(1.0, final_score)
        else:
            final_score = base_score

        return final_score

    def score_and_rank(
        self,
        landmarks: List[LandmarkEnhanced],
        vibes: List[str],
        group_type: str,
        min_score: float = 0.0,
        include_must_see: bool = True,
    ) -> List[LandmarkEnhanced]:
        """Score all landmarks and return sorted with reasons."""
        scored = []

        for landmark in landmarks:
            score = self.score_landmark(landmark, vibes, group_type)
            landmark.match_score = score
            landmark.selection_reason = self._generate_reason(
                landmark, vibes, group_type, score
            )
            scored.append(landmark)

        # Sort: iconic must-see first, then by score
        scored.sort(key=lambda x: (
            x.must_see_rating.tier == "iconic" and x.must_see_rating.is_must_see,
            x.must_see_rating.is_must_see,
            x.match_score,
        ), reverse=True)

        # Filter by min_score but always keep iconic
        if min_score > 0:
            scored = [
                lm for lm in scored
                if lm.match_score >= min_score
                or (include_must_see and lm.must_see_rating.is_must_see
                    and lm.must_see_rating.tier == "iconic")
            ]

        return scored

    def _calculate_vibe_score(
        self,
        vibe_scores: LandmarkVibeScores,
        selected_vibes: List[str],
    ) -> float:
        """Average score across selected vibes."""
        if not selected_vibes:
            return 0.5

        scores = []
        for vibe in selected_vibes:
            score = getattr(vibe_scores, vibe, None)
            if score is not None:
                scores.append(score)

        if not scores:
            return 0.5

        return sum(scores) / len(scores)

    def _generate_reason(
        self,
        landmark: LandmarkEnhanced,
        vibes: List[str],
        group_type: str,
        score: float,
    ) -> str:
        """Generate human-readable selection reason."""
        reasons = []

        if landmark.must_see_rating.is_must_see:
            if landmark.must_see_rating.tier == "iconic":
                reasons.append("Iconic must-see attraction")
            elif landmark.must_see_rating.tier == "recommended":
                reasons.append("Highly recommended attraction")

        if landmark.must_see_rating.reason:
            reasons.append(landmark.must_see_rating.reason)

        group_score = getattr(landmark.group_scores, group_type, 0.5)
        if group_score >= 0.8:
            reasons.append(f"Excellent match for {group_type} travelers")
        elif group_score >= 0.6:
            reasons.append(f"Good fit for {group_type} groups")

        matching_vibes = []
        for vibe in vibes:
            vibe_val = getattr(landmark.vibe_scores, vibe, 0.5)
            if vibe_val >= 0.7:
                matching_vibes.append(vibe)
        if matching_vibes:
            reasons.append(f"Strong {', '.join(matching_vibes)} vibes")

        if landmark.golden_hour_worthy and "photography" in vibes:
            reasons.append("Stunning at golden hour")

        if not reasons:
            reasons.append(f"Matches your {group_type} travel style")

        return "; ".join(reasons)
