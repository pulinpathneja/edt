import pytest
from httpx import AsyncClient


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


@pytest.mark.asyncio
async def test_list_pois_empty(client: AsyncClient):
    """Test listing POIs when database is empty."""
    response = await client.get("/api/v1/pois/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_list_itineraries_empty(client: AsyncClient):
    """Test listing itineraries when database is empty."""
    response = await client.get("/api/v1/itinerary/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_list_persona_templates_empty(client: AsyncClient):
    """Test listing persona templates when database is empty."""
    response = await client.get("/api/v1/personas/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
