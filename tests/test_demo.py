"""Tests for demo seed and reset endpoints."""
import uuid
import pytest
import pytest_asyncio
from datetime import datetime, date
from unittest.mock import MagicMock, AsyncMock, patch
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.user import DeviceSession, TripDraft, WishlistItem
from main import app

DEVICE_ID = "demo-test-device"
HEADERS = {"X-Device-ID": DEVICE_ID}


def _make_mock_session():
    obj = MagicMock(spec=DeviceSession)
    obj.id = uuid.uuid4()
    obj.device_id = DEVICE_ID
    obj.platform = "demo"
    obj.last_seen_at = datetime.utcnow()
    obj.created_at = datetime.utcnow()
    return obj


def _make_mock_draft():
    obj = MagicMock(spec=TripDraft)
    obj.id = uuid.uuid4()
    obj.device_id = DEVICE_ID
    obj.status = "active"
    obj.current_step = 2
    obj.country_id = "italy"
    obj.country_name = "Italy"
    obj.start_date = date(2026, 3, 20)
    obj.end_date = date(2026, 3, 29)
    obj.group_type = "couple"
    obj.group_size = 2
    obj.vibes = ["cultural", "romantic", "foodie"]
    obj.budget_level = 3
    obj.pacing = "moderate"
    obj.selected_allocation = None
    obj.created_at = datetime.utcnow()
    obj.updated_at = datetime.utcnow()
    return obj


@pytest_asyncio.fixture
async def demo_client():
    """Client with mock DB for demo endpoint testing."""
    mock_db = AsyncMock(spec=AsyncSession)

    # Default: return None for scalar_one_or_none, [] for scalars().all()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_result.scalars = MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.commit = AsyncMock()
    mock_db.rollback = AsyncMock()
    mock_db.refresh = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.delete = AsyncMock()

    async def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac, mock_db

    app.dependency_overrides.clear()


async def test_seed_creates_data(demo_client):
    """Seed creates a draft and wishlist items."""
    client, mock_db = demo_client

    response = await client.post("/api/v1/demo/seed", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "seeded"
    assert data["wishlist_items_added"] == 4

    # Verify db.add was called (session + draft + 4 wishlist items)
    assert mock_db.add.call_count >= 5


async def test_seed_skips_existing_wishlist(demo_client):
    """Seed skips duplicate wishlist items."""
    client, mock_db = demo_client

    existing_item = MagicMock(spec=WishlistItem)
    existing_item.id = uuid.uuid4()

    call_count = 0

    async def mock_execute(stmt):
        nonlocal call_count
        call_count += 1
        result = MagicMock()
        # First call: session lookup (None)
        # Second call: active drafts (empty)
        # Third+ calls: wishlist duplicate checks
        if call_count <= 2:
            result.scalar_one_or_none = MagicMock(return_value=None)
            result.scalars = MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))
        else:
            # Return existing for first wishlist item, None for rest
            if call_count == 3:
                result.scalar_one_or_none = MagicMock(return_value=existing_item)
            else:
                result.scalar_one_or_none = MagicMock(return_value=None)
        return result

    mock_db.execute = mock_execute

    response = await client.post("/api/v1/demo/seed", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["wishlist_items_added"] == 3  # 4 - 1 existing = 3


async def test_reset_clears_data(demo_client):
    """Reset deletes all drafts and wishlist items."""
    client, mock_db = demo_client

    response = await client.post("/api/v1/demo/reset", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "reset"

    # Verify execute was called (2 deletes) + commit
    assert mock_db.execute.call_count == 2
    mock_db.commit.assert_called()


async def test_seed_missing_header(demo_client):
    """Seed fails without X-Device-ID header."""
    client, _ = demo_client
    response = await client.post("/api/v1/demo/seed")
    assert response.status_code == 422


async def test_reset_missing_header(demo_client):
    """Reset fails without X-Device-ID header."""
    client, _ = demo_client
    response = await client.post("/api/v1/demo/reset")
    assert response.status_code == 422
