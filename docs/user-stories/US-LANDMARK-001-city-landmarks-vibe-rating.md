# User Story: City-Level Landmark Fetching with Vibe Ratings

## Story ID: US-LANDMARK-001
## Sprint: Current Sprint
## Priority: High
## Story Points: 8

---

## User Story

**As a** travel planner using the EDT system,
**I want to** fetch city-level landmarks with vibe ratings and must-see prioritization,
**So that** I can build personalized itineraries where iconic attractions are always included regardless of persona filters.

---

## Background

Currently, the system fetches landmarks from files or Wikidata but doesn't properly integrate them with the persona-based scoring system. The Colosseum in Rome wasn't appearing in honeymoon itineraries because its "romantic" vibe score was lower than other POIs.

**Key Insight**: Must-see landmarks (Eiffel Tower, Colosseum, Taj Mahal) should ALWAYS appear in itineraries regardless of persona - they're the reason people visit the city.

---

## Acceptance Criteria

### AC1: Landmark Data Model Enhancement
```gherkin
GIVEN a city landmark data file exists
WHEN the system loads landmarks
THEN each landmark MUST have:
  - Vibe scores for all 10 vibe categories (0.0-1.0)
  - A must_see rating (boolean + tier: "iconic", "recommended", "optional")
  - Persona group scores (family, honeymoon, solo, friends, etc.)
  - Typical duration by persona type
```

### AC2: Must-See Supersedes Everything
```gherkin
GIVEN a landmark is marked as must_see=true AND tier="iconic"
WHEN building an itinerary for ANY persona
THEN the landmark MUST be included in the itinerary
  AND it should appear on Day 1 or Day 2 at the latest
  AND its position should be optimized for best experience (morning/evening)
```

### AC3: Vibe-Based Ranking for Non-Must-See
```gherkin
GIVEN a list of landmarks with vibe scores
WHEN a user selects vibes: ["romantic", "cultural"]
THEN landmarks are ranked by:
  1. Must-see tier (iconic > recommended > optional)
  2. Average vibe score matching selected vibes
  3. Group type compatibility score
```

### AC4: Fetch Landmarks API Enhancement
```gherkin
GIVEN a request to GET /api/v1/landmarks/{city}
WHEN the request includes query params:
  - vibes: ["romantic", "foodie"]
  - group_type: "honeymoon"
  - include_must_see: true (default)
THEN the response returns landmarks:
  - Sorted with must-see landmarks first
  - Filtered/boosted by vibe compatibility
  - With computed match_score for the persona
```

### AC5: Landmark Scoring Integration
```gherkin
GIVEN the PersonaScorer processes landmarks
WHEN a landmark has must_see=true
THEN the final_score calculation:
  - Applies a +0.30 boost (superseding the current +0.15)
  - Sets minimum score floor of 0.70 (always competitive)
  - Adds selection_reason: "Iconic must-see attraction"
```

---

## Technical Design

### 1. Enhanced Landmark Schema

```python
# app/schemas/landmark.py - Enhanced Schema
class LandmarkVibeScores(BaseModel):
    """Vibe compatibility scores for a landmark."""
    romantic: float = Field(0.5, ge=0, le=1)
    cultural: float = Field(0.5, ge=0, le=1)
    adventure: float = Field(0.5, ge=0, le=1)
    relaxation: float = Field(0.5, ge=0, le=1)
    foodie: float = Field(0.5, ge=0, le=1)
    nightlife: float = Field(0.5, ge=0, le=1)
    nature: float = Field(0.5, ge=0, le=1)
    shopping: float = Field(0.5, ge=0, le=1)
    photography: float = Field(0.5, ge=0, le=1)
    spiritual: float = Field(0.5, ge=0, le=1)

class LandmarkGroupScores(BaseModel):
    """Group type compatibility scores."""
    family: float = Field(0.5, ge=0, le=1)
    honeymoon: float = Field(0.5, ge=0, le=1)
    solo: float = Field(0.5, ge=0, le=1)
    friends: float = Field(0.5, ge=0, le=1)
    seniors: float = Field(0.5, ge=0, le=1)
    business: float = Field(0.5, ge=0, le=1)

class MustSeeRating(BaseModel):
    """Must-see classification."""
    is_must_see: bool = True
    tier: Literal["iconic", "recommended", "optional"] = "recommended"
    reason: str = ""  # e.g., "UNESCO World Heritage Site"

class LandmarkEnhanced(BaseModel):
    """Enhanced landmark with full scoring data."""
    id: str
    name: str
    category: str
    latitude: float
    longitude: float
    description: str

    # Must-see rating (supersedes all other scores)
    must_see: MustSeeRating

    # Vibe compatibility scores
    vibe_scores: LandmarkVibeScores

    # Group compatibility scores
    group_scores: LandmarkGroupScores

    # Duration by persona (minutes)
    duration_by_persona: Dict[str, int] = {
        "default": 90,
        "family": 60,      # Shorter with kids
        "honeymoon": 75,   # Moderate
        "solo": 120,       # Can spend more time
        "seniors": 90,     # Standard pace
    }

    # Best times
    best_time: Literal["morning", "afternoon", "evening", "any"] = "any"
    golden_hour_worthy: bool = False

    # Computed at query time
    match_score: Optional[float] = None
    selection_reason: Optional[str] = None
```

### 2. Landmark Scoring Logic

```python
# app/services/landmark_scorer.py

class LandmarkScorer:
    """Scores landmarks with must-see prioritization."""

    # Must-see tier boosts
    MUST_SEE_BOOSTS = {
        "iconic": 0.35,      # Always appears, very high priority
        "recommended": 0.20, # Strong boost
        "optional": 0.05,    # Slight boost
    }

    # Minimum score floors by tier
    SCORE_FLOORS = {
        "iconic": 0.75,      # Never below 75%
        "recommended": 0.50, # Never below 50%
        "optional": 0.0,     # No floor
    }

    def score_landmark(
        self,
        landmark: LandmarkEnhanced,
        vibes: List[str],
        group_type: str,
    ) -> float:
        """
        Calculate final score with must-see prioritization.

        Priority order:
        1. Must-see tier (iconic landmarks always win)
        2. Vibe compatibility
        3. Group compatibility
        """
        # Base vibe score (average of selected vibes)
        vibe_score = self._calculate_vibe_score(landmark.vibe_scores, vibes)

        # Group compatibility score
        group_score = getattr(landmark.group_scores, group_type, 0.5)

        # Weighted combination (before must-see boost)
        base_score = (vibe_score * 0.5) + (group_score * 0.5)

        # Apply must-see boost
        if landmark.must_see.is_must_see:
            tier = landmark.must_see.tier
            boost = self.MUST_SEE_BOOSTS.get(tier, 0)
            floor = self.SCORE_FLOORS.get(tier, 0)

            # Apply boost
            boosted_score = base_score + boost

            # Apply floor (minimum score)
            final_score = max(floor, boosted_score)

            # Cap at 1.0
            final_score = min(1.0, final_score)
        else:
            final_score = base_score

        return final_score

    def _calculate_vibe_score(
        self,
        vibe_scores: LandmarkVibeScores,
        selected_vibes: List[str]
    ) -> float:
        """Average score across selected vibes."""
        if not selected_vibes:
            return 0.5

        scores = []
        for vibe in selected_vibes:
            score = getattr(vibe_scores, vibe, 0.5)
            scores.append(score)

        return sum(scores) / len(scores)
```

### 3. Enhanced Landmark JSON Format

```json
// data/landmarks/rome_landmarks.json
[
  {
    "id": "rome_colosseum",
    "name": "Colosseum",
    "category": "historical",
    "latitude": 41.8902,
    "longitude": 12.4922,
    "description": "Ancient Roman amphitheater, icon of Imperial Rome",

    "must_see": {
      "is_must_see": true,
      "tier": "iconic",
      "reason": "UNESCO World Heritage Site, Symbol of Rome"
    },

    "vibe_scores": {
      "romantic": 0.70,
      "cultural": 0.95,
      "adventure": 0.60,
      "relaxation": 0.30,
      "foodie": 0.20,
      "nightlife": 0.40,
      "nature": 0.20,
      "shopping": 0.10,
      "photography": 0.95,
      "spiritual": 0.40
    },

    "group_scores": {
      "family": 0.85,
      "honeymoon": 0.80,
      "solo": 0.90,
      "friends": 0.85,
      "seniors": 0.75,
      "business": 0.60
    },

    "duration_by_persona": {
      "default": 120,
      "family": 90,
      "honeymoon": 90,
      "solo": 150,
      "seniors": 120
    },

    "best_time": "morning",
    "golden_hour_worthy": true
  },
  {
    "id": "rome_trevi",
    "name": "Trevi Fountain",
    "category": "monument",
    "latitude": 41.9009,
    "longitude": 12.4833,
    "description": "Baroque masterpiece, make a wish tradition",

    "must_see": {
      "is_must_see": true,
      "tier": "iconic",
      "reason": "Most famous fountain in the world"
    },

    "vibe_scores": {
      "romantic": 0.98,
      "cultural": 0.85,
      "adventure": 0.30,
      "relaxation": 0.60,
      "foodie": 0.40,
      "nightlife": 0.70,
      "nature": 0.20,
      "shopping": 0.50,
      "photography": 0.95,
      "spiritual": 0.50
    },

    "group_scores": {
      "family": 0.80,
      "honeymoon": 0.98,
      "solo": 0.85,
      "friends": 0.90,
      "seniors": 0.85,
      "business": 0.70
    },

    "duration_by_persona": {
      "default": 45,
      "family": 30,
      "honeymoon": 60,
      "solo": 45,
      "seniors": 45
    },

    "best_time": "evening",
    "golden_hour_worthy": true
  }
]
```

### 4. API Endpoint Enhancement

```python
# app/api/routes/landmarks.py - Enhanced endpoint

@router.get("/{city_id}/scored", response_model=ScoredLandmarkListResponse)
async def get_scored_landmarks(
    city_id: str,
    vibes: List[str] = Query(default=["cultural"]),
    group_type: str = Query(default="solo"),
    include_must_see: bool = Query(default=True),
    min_score: float = Query(default=0.0, ge=0, le=1),
    limit: int = Query(default=20, ge=1, le=50),
):
    """
    Get landmarks with persona-based scoring.

    Must-see landmarks (tier=iconic) are ALWAYS included
    regardless of min_score filter.
    """
    # Load landmarks
    landmarks = load_enhanced_landmarks(city_id)

    # Score all landmarks
    scorer = LandmarkScorer()
    scored = []

    for landmark in landmarks:
        score = scorer.score_landmark(landmark, vibes, group_type)
        landmark.match_score = score
        landmark.selection_reason = generate_reason(landmark, vibes, group_type)
        scored.append(landmark)

    # Sort: must-see iconic first, then by score
    scored.sort(key=lambda x: (
        x.must_see.tier == "iconic",  # Iconic first
        x.must_see.is_must_see,       # Then must-see
        x.match_score                  # Then by score
    ), reverse=True)

    # Filter by min_score but ALWAYS include iconic
    if min_score > 0:
        scored = [
            lm for lm in scored
            if lm.match_score >= min_score
            or (lm.must_see.is_must_see and lm.must_see.tier == "iconic")
        ]

    return ScoredLandmarkListResponse(
        city=city_id,
        vibes=vibes,
        group_type=group_type,
        landmarks=scored[:limit],
        total=len(scored[:limit]),
    )
```

---

## Implementation Tasks

### Task 1: Schema Updates (2 pts)
- [ ] Create `LandmarkVibeScores` schema
- [ ] Create `LandmarkGroupScores` schema
- [ ] Create `MustSeeRating` schema
- [ ] Create `LandmarkEnhanced` schema
- [ ] Update `LandmarkResponse` to include new fields

### Task 2: Landmark Scorer Service (3 pts)
- [ ] Create `app/services/landmark_scorer.py`
- [ ] Implement `score_landmark()` with must-see prioritization
- [ ] Implement vibe score calculation
- [ ] Implement group score calculation
- [ ] Add score floor logic for iconic landmarks
- [ ] Write unit tests

### Task 3: Data Migration (2 pts)
- [ ] Update `rome_landmarks.json` with vibe scores
- [ ] Update `paris_landmarks.json` with vibe scores
- [ ] Create script to enrich landmarks with Gemini LLM
- [ ] Validate all iconic landmarks have proper ratings

### Task 4: API Enhancement (1 pt)
- [ ] Add `/landmarks/{city}/scored` endpoint
- [ ] Add query params: vibes, group_type, include_must_see
- [ ] Update response schema with match_score
- [ ] Add integration tests

---

## Test Cases

### TC1: Iconic Landmark Always Appears
```python
def test_colosseum_appears_in_honeymoon_itinerary():
    response = client.get(
        "/api/v1/landmarks/rome/scored",
        params={"vibes": ["romantic"], "group_type": "honeymoon"}
    )
    landmarks = response.json()["landmarks"]

    # Colosseum must be in the list
    colosseum = next(lm for lm in landmarks if "Colosseum" in lm["name"])
    assert colosseum is not None
    assert colosseum["must_see"]["tier"] == "iconic"
    assert colosseum["match_score"] >= 0.75  # Floor for iconic
```

### TC2: Must-See Boost Applied
```python
def test_must_see_boost_applied():
    scorer = LandmarkScorer()

    # Landmark with low vibe match but iconic status
    landmark = LandmarkEnhanced(
        id="test",
        name="Test Landmark",
        must_see=MustSeeRating(is_must_see=True, tier="iconic"),
        vibe_scores=LandmarkVibeScores(romantic=0.3),  # Low romantic
        group_scores=LandmarkGroupScores(honeymoon=0.4),  # Low honeymoon
    )

    score = scorer.score_landmark(landmark, ["romantic"], "honeymoon")

    # Despite low vibe/group scores, should be >= 0.75 (iconic floor)
    assert score >= 0.75
```

### TC3: Vibe Ranking for Non-Must-See
```python
def test_vibe_ranking_for_optional_landmarks():
    landmarks = [
        create_landmark(name="Romantic Spot", romantic=0.9, tier="optional"),
        create_landmark(name="Cultural Spot", cultural=0.9, tier="optional"),
    ]

    scorer = LandmarkScorer()
    scores = [
        scorer.score_landmark(lm, ["romantic"], "honeymoon")
        for lm in landmarks
    ]

    # Romantic Spot should score higher for romantic vibe
    assert scores[0] > scores[1]
```

---

## Definition of Done

- [ ] All acceptance criteria pass
- [ ] Unit tests written and passing (>80% coverage)
- [ ] Integration tests for new endpoint
- [ ] Rome and Paris landmarks updated with vibe scores
- [ ] API documentation updated in Swagger
- [ ] Code reviewed and merged
- [ ] Deployed to staging environment
- [ ] Tested with real itinerary generation

---

## Dependencies

- Existing landmark files in `data/landmarks/`
- PersonaScorer in `app/services/rag/scorer.py`
- Gemini API for LLM-based landmark enrichment (optional)

---

## Notes

1. **Score Floor Logic**: Iconic landmarks use a score floor (minimum 0.75) to ensure they're always competitive, even if persona doesn't match perfectly.

2. **Superseding Behavior**: The `must_see.tier == "iconic"` check happens AFTER scoring, ensuring iconic landmarks bypass min_score filters.

3. **LLM Enrichment**: For new cities, use Gemini to generate initial vibe scores based on landmark descriptions, then manually curate iconic landmarks.

4. **Duration by Persona**: Family visits are shorter (kids get bored), solo travelers can spend longer exploring.
