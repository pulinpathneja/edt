import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_scored_landmarks_default(client: AsyncClient):
    """Test scored landmarks endpoint with default params."""
    response = await client.get("/api/v1/landmarks/rome/scored")
    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "rome"
    assert data["total"] > 0
    assert len(data["landmarks"]) > 0

    first = data["landmarks"][0]
    assert "match_score" in first
    assert "selection_reason" in first
    assert "must_see_rating" in first
    assert "vibe_scores" in first
    assert "group_scores" in first


@pytest.mark.asyncio
async def test_scored_landmarks_honeymoon(client: AsyncClient):
    """Test scored landmarks for honeymoon couple."""
    response = await client.get(
        "/api/v1/landmarks/rome/scored",
        params={"vibes": ["romantic"], "group_type": "honeymoon"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["group_type"] == "honeymoon"
    assert data["vibes"] == ["romantic"]

    # Trevi Fountain should score very high for romantic honeymoon
    trevi = next(
        (lm for lm in data["landmarks"] if "Trevi" in lm["name"]),
        None,
    )
    assert trevi is not None
    assert trevi["match_score"] >= 0.75


@pytest.mark.asyncio
async def test_colosseum_appears_in_all_personas(client: AsyncClient):
    """Iconic landmarks like Colosseum should appear for all personas."""
    personas = [
        (["romantic"], "honeymoon"),
        (["adventure"], "solo"),
        (["foodie"], "friends"),
        (["relaxation"], "seniors"),
        (["cultural"], "family"),
    ]

    for vibes, group in personas:
        response = await client.get(
            "/api/v1/landmarks/rome/scored",
            params={"vibes": vibes, "group_type": group},
        )
        data = response.json()
        names = [lm["name"] for lm in data["landmarks"]]
        assert "Colosseum" in names, (
            f"Colosseum missing for {group} + {vibes}"
        )

        colosseum = next(lm for lm in data["landmarks"] if lm["name"] == "Colosseum")
        assert colosseum["match_score"] >= 0.75


@pytest.mark.asyncio
async def test_scored_landmarks_with_min_score(client: AsyncClient):
    """min_score filter should work but keep iconic landmarks."""
    response = await client.get(
        "/api/v1/landmarks/rome/scored",
        params={"vibes": ["nightlife"], "group_type": "friends", "min_score": 0.7},
    )
    assert response.status_code == 200
    data = response.json()

    for lm in data["landmarks"]:
        # Either above min_score or iconic must-see
        is_iconic = (
            lm["must_see_rating"]["is_must_see"]
            and lm["must_see_rating"]["tier"] == "iconic"
        )
        assert lm["match_score"] >= 0.7 or is_iconic


@pytest.mark.asyncio
async def test_scored_landmarks_limit(client: AsyncClient):
    """Limit parameter should cap results."""
    response = await client.get(
        "/api/v1/landmarks/rome/scored",
        params={"limit": 3},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["landmarks"]) <= 3


@pytest.mark.asyncio
async def test_scored_landmarks_404_unknown_city(client: AsyncClient):
    """Unknown city should return 404."""
    response = await client.get("/api/v1/landmarks/atlantis/scored")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_scored_landmarks_response_shape(client: AsyncClient):
    """Verify full response structure."""
    response = await client.get(
        "/api/v1/landmarks/rome/scored",
        params={"vibes": ["cultural", "photography"], "group_type": "solo"},
    )
    assert response.status_code == 200
    data = response.json()

    landmark = data["landmarks"][0]

    # Check nested structures
    assert "romantic" in landmark["vibe_scores"]
    assert "cultural" in landmark["vibe_scores"]
    assert "family" in landmark["group_scores"]
    assert "honeymoon" in landmark["group_scores"]
    assert "tier" in landmark["must_see_rating"]
    assert "is_must_see" in landmark["must_see_rating"]
    assert "duration_by_persona" in landmark
    assert "best_time" in landmark
    assert isinstance(landmark["match_score"], float)
    assert 0 <= landmark["match_score"] <= 1
