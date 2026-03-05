import pytest
from app.services.landmark_scorer import LandmarkScorer
from app.schemas.landmark import (
    LandmarkEnhanced,
    LandmarkVibeScores,
    LandmarkGroupScores,
    MustSeeRating,
)


def make_landmark(
    name: str = "Test Landmark",
    is_must_see: bool = False,
    tier: str = "optional",
    reason: str = "",
    vibe_overrides: dict = None,
    group_overrides: dict = None,
) -> LandmarkEnhanced:
    """Helper to create a test landmark."""
    vibe_kwargs = vibe_overrides or {}
    group_kwargs = group_overrides or {}
    return LandmarkEnhanced(
        id=f"test_{name.lower().replace(' ', '_')}",
        name=name,
        category="attraction",
        latitude=41.89,
        longitude=12.49,
        description=f"Test landmark: {name}",
        must_see_rating=MustSeeRating(
            is_must_see=is_must_see,
            tier=tier,
            reason=reason,
        ),
        vibe_scores=LandmarkVibeScores(**vibe_kwargs),
        group_scores=LandmarkGroupScores(**group_kwargs),
        duration_by_persona={"default": 90},
        best_time="any",
        golden_hour_worthy=False,
    )


class TestLandmarkScorer:
    """Unit tests for LandmarkScorer."""

    def setup_method(self):
        self.scorer = LandmarkScorer()

    # ---- TC1: Iconic landmark always has high score ----

    def test_iconic_landmark_score_floor(self):
        """Iconic landmarks should never score below 0.75, even with low vibe/group match."""
        landmark = make_landmark(
            name="Colosseum",
            is_must_see=True,
            tier="iconic",
            vibe_overrides={"romantic": 0.3},
            group_overrides={"honeymoon": 0.4},
        )

        score = self.scorer.score_landmark(landmark, ["romantic"], "honeymoon")
        assert score >= 0.75, f"Iconic landmark scored {score}, expected >= 0.75"

    def test_iconic_landmark_with_high_match(self):
        """Iconic + high vibe match should score near 1.0."""
        landmark = make_landmark(
            name="Trevi Fountain",
            is_must_see=True,
            tier="iconic",
            vibe_overrides={"romantic": 0.98},
            group_overrides={"honeymoon": 0.98},
        )

        score = self.scorer.score_landmark(landmark, ["romantic"], "honeymoon")
        assert score >= 0.95

    # ---- TC2: Must-see boost applied correctly ----

    def test_must_see_boost_iconic(self):
        """Iconic tier should get +0.35 boost."""
        landmark = make_landmark(is_must_see=True, tier="iconic")
        score_with = self.scorer.score_landmark(landmark, ["cultural"], "solo")

        landmark_no_boost = make_landmark(is_must_see=False, tier="optional")
        score_without = self.scorer.score_landmark(landmark_no_boost, ["cultural"], "solo")

        assert score_with > score_without

    def test_must_see_boost_recommended(self):
        """Recommended tier should get +0.20 boost."""
        landmark = make_landmark(is_must_see=True, tier="recommended")
        score = self.scorer.score_landmark(landmark, ["cultural"], "solo")

        landmark_optional = make_landmark(is_must_see=False, tier="optional")
        score_optional = self.scorer.score_landmark(landmark_optional, ["cultural"], "solo")

        assert score > score_optional

    def test_recommended_score_floor(self):
        """Recommended tier should have 0.50 floor."""
        landmark = make_landmark(
            is_must_see=True,
            tier="recommended",
            vibe_overrides={"romantic": 0.1},
            group_overrides={"business": 0.1},
        )

        score = self.scorer.score_landmark(landmark, ["romantic"], "business")
        assert score >= 0.50

    # ---- TC3: Vibe ranking for non-must-see ----

    def test_vibe_ranking_non_must_see(self):
        """Higher vibe match should score higher for optional landmarks."""
        romantic_spot = make_landmark(
            name="Romantic Spot",
            vibe_overrides={"romantic": 0.9},
            group_overrides={"honeymoon": 0.8},
        )
        cultural_spot = make_landmark(
            name="Cultural Spot",
            vibe_overrides={"romantic": 0.2, "cultural": 0.9},
            group_overrides={"honeymoon": 0.5},
        )

        score_romantic = self.scorer.score_landmark(romantic_spot, ["romantic"], "honeymoon")
        score_cultural = self.scorer.score_landmark(cultural_spot, ["romantic"], "honeymoon")

        assert score_romantic > score_cultural

    def test_multi_vibe_averaging(self):
        """Multiple vibes should average their scores."""
        landmark = make_landmark(
            vibe_overrides={"romantic": 0.9, "cultural": 0.3},
        )

        # When both vibes selected, should average
        score = self.scorer.score_landmark(landmark, ["romantic", "cultural"], "solo")

        # Average vibe = (0.9 + 0.3) / 2 = 0.6
        # Group = 0.5 (default)
        # Base = 0.6 * 0.5 + 0.5 * 0.5 = 0.55
        assert 0.4 <= score <= 0.7

    # ---- TC4: Group type scoring ----

    def test_group_type_affects_score(self):
        """Different group types should yield different scores."""
        landmark = make_landmark(
            group_overrides={"family": 0.95, "business": 0.2},
        )

        family_score = self.scorer.score_landmark(landmark, ["cultural"], "family")
        business_score = self.scorer.score_landmark(landmark, ["cultural"], "business")

        assert family_score > business_score

    # ---- TC5: score_and_rank sorting ----

    def test_score_and_rank_iconic_first(self):
        """Iconic landmarks should appear before non-iconic in ranked results."""
        landmarks = [
            make_landmark(
                name="Hidden Gem",
                vibe_overrides={"romantic": 0.99},
                group_overrides={"honeymoon": 0.99},
            ),
            make_landmark(
                name="Colosseum",
                is_must_see=True,
                tier="iconic",
                vibe_overrides={"romantic": 0.5},
                group_overrides={"honeymoon": 0.5},
            ),
        ]

        ranked = self.scorer.score_and_rank(landmarks, ["romantic"], "honeymoon")

        assert ranked[0].name == "Colosseum"

    def test_score_and_rank_min_score_filter(self):
        """min_score filter should exclude low scorers but keep iconic."""
        landmarks = [
            make_landmark(
                name="Iconic Place",
                is_must_see=True,
                tier="iconic",
                vibe_overrides={"romantic": 0.3},
                group_overrides={"solo": 0.3},
            ),
            make_landmark(
                name="Low Scorer",
                vibe_overrides={"romantic": 0.1},
                group_overrides={"solo": 0.1},
            ),
        ]

        ranked = self.scorer.score_and_rank(
            landmarks, ["romantic"], "solo", min_score=0.7
        )

        names = [lm.name for lm in ranked]
        assert "Iconic Place" in names
        assert "Low Scorer" not in names

    # ---- TC6: Selection reason generation ----

    def test_selection_reason_iconic(self):
        """Iconic landmarks should have 'Iconic must-see attraction' in reason."""
        landmark = make_landmark(
            is_must_see=True,
            tier="iconic",
            reason="UNESCO World Heritage Site",
        )

        self.scorer.score_and_rank([landmark], ["cultural"], "solo")
        assert "Iconic must-see attraction" in landmark.selection_reason
        assert "UNESCO World Heritage Site" in landmark.selection_reason

    def test_selection_reason_vibe_match(self):
        """Strong vibe matches should appear in selection reason."""
        landmark = make_landmark(vibe_overrides={"romantic": 0.9})

        self.scorer.score_and_rank([landmark], ["romantic"], "honeymoon")
        assert "romantic" in landmark.selection_reason.lower()

    # ---- Edge cases ----

    def test_empty_vibes_list(self):
        """Empty vibes should default to 0.5 vibe score."""
        landmark = make_landmark()
        score = self.scorer.score_landmark(landmark, [], "solo")
        assert 0.0 <= score <= 1.0

    def test_unknown_group_type(self):
        """Unknown group type should default to 0.5."""
        landmark = make_landmark()
        score = self.scorer.score_landmark(landmark, ["cultural"], "unknown_type")
        assert 0.0 <= score <= 1.0

    def test_score_capped_at_one(self):
        """Score should never exceed 1.0."""
        landmark = make_landmark(
            is_must_see=True,
            tier="iconic",
            vibe_overrides={"romantic": 1.0, "cultural": 1.0},
            group_overrides={"honeymoon": 1.0},
        )

        score = self.scorer.score_landmark(landmark, ["romantic", "cultural"], "honeymoon")
        assert score <= 1.0
