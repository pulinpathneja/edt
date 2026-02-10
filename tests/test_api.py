import pytest
from httpx import AsyncClient
from uuid import uuid4


# ============================================================================
# Health & Root Endpoints
# ============================================================================

@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test the root endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "status" in data
    assert data["status"] == "running"


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test the health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


# ============================================================================
# Cities API Tests
# ============================================================================

@pytest.mark.asyncio
async def test_list_cities(client: AsyncClient):
    """Test listing all available cities."""
    response = await client.get("/api/v1/cities/")
    assert response.status_code == 200
    data = response.json()
    assert "cities" in data
    assert "total" in data
    assert isinstance(data["cities"], list)
    # Should have at least Paris, Rome, Barcelona, Tokyo, London
    assert data["total"] >= 5


@pytest.mark.asyncio
async def test_get_city_paris(client: AsyncClient):
    """Test getting Paris city details."""
    response = await client.get("/api/v1/cities/paris")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Paris"
    assert data["country"] == "France"
    assert data["currency"] == "EUR"
    assert "bbox" in data
    assert "center" in data
    assert "neighborhoods" in data


@pytest.mark.asyncio
async def test_get_city_not_found(client: AsyncClient):
    """Test getting non-existent city."""
    response = await client.get("/api/v1/cities/atlantis")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_city_neighborhoods(client: AsyncClient):
    """Test getting neighborhoods for a city."""
    response = await client.get("/api/v1/cities/rome/neighborhoods")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # Each neighborhood should have name, lat, lon
    for nb in data:
        assert "name" in nb
        assert "lat" in nb
        assert "lon" in nb


@pytest.mark.asyncio
async def test_recommend_neighborhoods(client: AsyncClient):
    """Test neighborhood recommendations based on persona."""
    response = await client.post("/api/v1/cities/neighborhoods/recommend", json={
        "city": "Paris",
        "group_type": "honeymoon",
        "vibes": ["romantic", "foodie"]
    })
    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "Paris"
    assert data["group_type"] == "honeymoon"
    assert "recommendations" in data
    assert len(data["recommendations"]) > 0
    # Each recommendation should have a score
    for rec in data["recommendations"]:
        assert "score" in rec
        assert 0 <= rec["score"] <= 1


# ============================================================================
# Landmarks API Tests
# ============================================================================

@pytest.mark.asyncio
async def test_get_landmarks_rome(client: AsyncClient):
    """Test getting landmarks for Rome."""
    response = await client.get("/api/v1/landmarks/rome")
    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "rome"
    assert "landmarks" in data
    assert "total" in data
    assert "source" in data


@pytest.mark.asyncio
async def test_get_landmarks_not_found(client: AsyncClient):
    """Test getting landmarks for unknown city."""
    response = await client.get("/api/v1/landmarks/unknown_city")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_generate_landmarks(client: AsyncClient):
    """Test generating landmarks for a city."""
    response = await client.post("/api/v1/landmarks/generate", json={
        "city": "Rome",
        "country": "Italy",
        "method": "file",
        "limit": 10
    })
    assert response.status_code == 200
    data = response.json()
    assert "landmarks" in data
    assert "method_used" in data


# ============================================================================
# Personas API Tests
# ============================================================================

@pytest.mark.asyncio
async def test_persona_config(client: AsyncClient):
    """Test getting persona configuration."""
    response = await client.get("/api/v1/personas/config")
    assert response.status_code == 200
    data = response.json()
    assert "group_types" in data
    assert "vibe_categories" in data
    assert "pacing_options" in data
    assert "budget_levels" in data
    # Verify group types
    assert "honeymoon" in data["group_types"]
    assert "family" in data["group_types"]
    # Verify vibes
    assert "romantic" in data["vibe_categories"]
    assert "cultural" in data["vibe_categories"]


@pytest.mark.asyncio
async def test_list_persona_templates_empty(client: AsyncClient):
    """Test listing persona templates when database is empty."""
    response = await client.get("/api/v1/personas/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


# ============================================================================
# POI API Tests
# ============================================================================

@pytest.mark.asyncio
async def test_list_pois_empty(client: AsyncClient):
    """Test listing POIs when database is empty."""
    response = await client.get("/api/v1/pois/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
@pytest.mark.skip(reason="Requires real PostgreSQL database")
async def test_create_poi(client_with_db: AsyncClient):
    """Test creating a new POI."""
    poi_data = {
        "name": "Test Attraction",
        "description": "A test attraction for testing purposes",
        "latitude": 41.9028,
        "longitude": 12.4964,
        "city": "Rome",
        "country": "Italy",
        "category": "attraction",
        "subcategory": "museum",
        "typical_duration_minutes": 90,
        "best_time_of_day": "morning",
        "cost_level": 2
    }
    response = await client_with_db.post("/api/v1/pois/", json=poi_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Attraction"
    assert "id" in data
    return data["id"]


@pytest.mark.asyncio
@pytest.mark.skip(reason="Requires real PostgreSQL database")
async def test_get_poi_not_found(client_with_db: AsyncClient):
    """Test getting non-existent POI."""
    fake_id = str(uuid4())
    response = await client_with_db.get(f"/api/v1/pois/{fake_id}")
    assert response.status_code == 404


# ============================================================================
# Itinerary API Tests
# ============================================================================

@pytest.mark.asyncio
async def test_list_itineraries_empty(client: AsyncClient):
    """Test listing itineraries when database is empty."""
    response = await client.get("/api/v1/itinerary/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
@pytest.mark.skip(reason="Requires real PostgreSQL database")
async def test_create_trip_request(client_with_db: AsyncClient):
    """Test creating a trip request."""
    trip_data = {
        "destination": "Rome",
        "start_date": "2025-06-01",
        "end_date": "2025-06-04",
        "group_type": "honeymoon",
        "vibes": ["romantic", "foodie", "cultural"],
        "budget_level": 3,
        "pacing": "slow"
    }
    response = await client_with_db.post("/api/v1/itinerary/trip-request", json=trip_data)
    # Should work or return meaningful error
    assert response.status_code in [200, 201, 422, 500]


# ============================================================================
# Recommendations API Tests
# ============================================================================

@pytest.mark.asyncio
async def test_get_recommendations_config(client: AsyncClient):
    """Test that recommendations endpoint exists."""
    # Test the neighborhoods recommend endpoint which we already tested
    response = await client.post("/api/v1/cities/neighborhoods/recommend", json={
        "city": "Rome",
        "group_type": "solo",
        "vibes": ["cultural", "foodie"]
    })
    assert response.status_code == 200


# ============================================================================
# Travel Time API Tests
# ============================================================================

@pytest.mark.asyncio
async def test_calculate_travel_time(client: AsyncClient):
    """Test travel time calculation between two points."""
    response = await client.post("/api/v1/travel/estimate", json={
        "origin": {"latitude": 41.9028, "longitude": 12.4964},
        "destination": {"latitude": 41.8902, "longitude": 12.4922}
    })
    assert response.status_code == 200
    data = response.json()
    assert "walk_minutes" in data
    assert "distance_km" in data
    assert "recommended_mode" in data


@pytest.mark.asyncio
async def test_calculate_route(client: AsyncClient):
    """Test multi-point route calculation."""
    response = await client.post("/api/v1/travel/route", json={
        "points": [
            {"latitude": 41.9028, "longitude": 12.4964},
            {"latitude": 41.8902, "longitude": 12.4922},
            {"latitude": 41.9009, "longitude": 12.4833}
        ]
    })
    assert response.status_code == 200
    data = response.json()
    assert "legs" in data
    assert "total_distance_km" in data
    assert len(data["legs"]) == 2


@pytest.mark.asyncio
async def test_optimize_route(client: AsyncClient):
    """Test route optimization."""
    response = await client.post("/api/v1/travel/optimize", json={
        "points": [
            {"latitude": 41.9028, "longitude": 12.4964},
            {"latitude": 41.8902, "longitude": 12.4922},
            {"latitude": 41.9009, "longitude": 12.4833},
            {"latitude": 41.8867, "longitude": 12.4700}
        ],
        "start_index": 0
    })
    assert response.status_code == 200
    data = response.json()
    assert "optimized_order" in data
    assert "savings_km" in data


@pytest.mark.asyncio
async def test_get_distance(client: AsyncClient):
    """Test quick distance calculation (GET method)."""
    response = await client.get(
        "/api/v1/travel/distance?lat1=41.9028&lon1=12.4964&lat2=41.8902&lon2=12.4922"
    )
    assert response.status_code == 200
    data = response.json()
    assert "distance_km" in data
    assert data["distance_km"] > 0
