"""Tests for session, draft, and wishlist features."""
import uuid
import pytest
import pytest_asyncio
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock, patch
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.user import DeviceSession, TripDraft, WishlistItem
from main import app

DEVICE_ID = "test-device-abc123"
HEADERS = {"X-Device-ID": DEVICE_ID}


def _make_mock_session_obj():
    """Create a mock DeviceSession with valid attributes."""
    obj = MagicMock(spec=DeviceSession)
    obj.id = uuid.uuid4()
    obj.device_id = DEVICE_ID
    obj.platform = "ios"
    obj.app_version = "1.0.0"
    obj.last_seen_at = datetime.utcnow()
    obj.created_at = datetime.utcnow()
    return obj


def _make_mock_draft():
    """Create a mock TripDraft."""
    obj = MagicMock(spec=TripDraft)
    obj.id = uuid.uuid4()
    obj.device_id = DEVICE_ID
    obj.status = "active"
    obj.current_step = 1
    obj.country_id = "italy"
    obj.country_name = "Italy"
    obj.start_date = None
    obj.end_date = None
    obj.group_type = "couple"
    obj.group_size = 2
    obj.vibes = ["cultural", "foodie"]
    obj.budget_level = 3
    obj.pacing = "moderate"
    obj.selected_allocation = None
    obj.created_at = datetime.utcnow()
    obj.updated_at = datetime.utcnow()
    return obj


def _make_mock_wishlist_item():
    """Create a mock WishlistItem."""
    obj = MagicMock(spec=WishlistItem)
    obj.id = uuid.uuid4()
    obj.device_id = DEVICE_ID
    obj.poi_name = "Colosseum"
    obj.city = "Rome"
    obj.country = "Italy"
    obj.category = "sightseeing"
    obj.image_url = None
    obj.description = None
    obj.created_at = datetime.utcnow()
    return obj


@pytest_asyncio.fixture
async def user_client():
    """Client with mock DB that returns None for scalar_one_or_none by default."""
    mock_db = AsyncMock(spec=AsyncSession)

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


# ============== Session Tests ==============

async def test_register_session_creates_new(user_client):
    """Register creates a new session when device not found."""
    client, mock_db = user_client
    mock_session = _make_mock_session_obj()

    # scalar_one_or_none returns None (no existing session)
    # After add+commit, refresh should populate the object
    async def mock_refresh(obj):
        for attr in ['id', 'device_id', 'platform', 'app_version', 'last_seen_at', 'created_at']:
            setattr(obj, attr, getattr(mock_session, attr))

    mock_db.refresh = mock_refresh

    response = await client.post(
        "/api/v1/sessions/register",
        json={"platform": "ios", "app_version": "1.0.0"},
        headers=HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["device_id"] == DEVICE_ID


async def test_register_session_updates_existing(user_client):
    """Register updates last_seen when session exists."""
    client, mock_db = user_client
    existing = _make_mock_session_obj()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=existing)
    mock_db.execute = AsyncMock(return_value=mock_result)

    async def mock_refresh(obj):
        pass  # existing object already has attributes

    mock_db.refresh = mock_refresh

    response = await client.post(
        "/api/v1/sessions/register",
        json={"platform": "ios"},
        headers=HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["device_id"] == DEVICE_ID


async def test_register_session_missing_header(user_client):
    """Should fail without X-Device-ID header."""
    client, _ = user_client
    response = await client.post("/api/v1/sessions/register", json={})
    assert response.status_code == 422


# ============== Draft Tests ==============

async def test_get_active_draft_empty(user_client):
    """No active draft returns null."""
    client, _ = user_client
    response = await client.get("/api/v1/drafts/active", headers=HEADERS)
    assert response.status_code == 200
    assert response.json() is None


async def test_get_active_draft_returns_draft(user_client):
    """Returns the active draft when one exists."""
    client, mock_db = user_client
    draft = _make_mock_draft()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=draft)
    mock_db.execute = AsyncMock(return_value=mock_result)

    response = await client.get("/api/v1/drafts/active", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["country_id"] == "italy"
    assert data["status"] == "active"


async def test_create_draft(user_client):
    """Create a new trip draft."""
    client, mock_db = user_client
    draft = _make_mock_draft()

    async def mock_refresh(obj):
        for attr in ['id', 'device_id', 'status', 'current_step', 'country_id',
                      'country_name', 'start_date', 'end_date', 'group_type',
                      'group_size', 'vibes', 'budget_level', 'pacing',
                      'selected_allocation', 'created_at', 'updated_at']:
            setattr(obj, attr, getattr(draft, attr))

    mock_db.refresh = mock_refresh

    response = await client.post(
        "/api/v1/drafts/",
        json={"current_step": 1, "country_id": "italy", "country_name": "Italy"},
        headers=HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["country_id"] == "italy"


async def test_delete_draft_not_found(user_client):
    """Deleting non-existent draft returns 404."""
    client, _ = user_client
    response = await client.delete(
        "/api/v1/drafts/00000000-0000-0000-0000-000000000000",
        headers=HEADERS,
    )
    assert response.status_code == 404


async def test_draft_missing_header(user_client):
    """Draft creation fails without device ID."""
    client, _ = user_client
    response = await client.post("/api/v1/drafts/", json={"current_step": 0})
    assert response.status_code == 422


# ============== Wishlist Tests ==============

async def test_list_wishlist_empty(user_client):
    """Empty wishlist returns empty list."""
    client, _ = user_client
    response = await client.get("/api/v1/wishlist/", headers=HEADERS)
    assert response.status_code == 200
    assert response.json() == []


async def test_list_wishlist_with_items(user_client):
    """Returns wishlist items."""
    client, mock_db = user_client
    item = _make_mock_wishlist_item()

    mock_result = MagicMock()
    mock_result.scalars = MagicMock(return_value=MagicMock(all=MagicMock(return_value=[item])))
    mock_db.execute = AsyncMock(return_value=mock_result)

    response = await client.get("/api/v1/wishlist/", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["poi_name"] == "Colosseum"


async def test_add_to_wishlist(user_client):
    """Add item to wishlist."""
    client, mock_db = user_client
    item = _make_mock_wishlist_item()

    async def mock_refresh(obj):
        for attr in ['id', 'device_id', 'poi_name', 'city', 'country',
                      'category', 'image_url', 'description', 'created_at']:
            setattr(obj, attr, getattr(item, attr))

    mock_db.refresh = mock_refresh

    response = await client.post(
        "/api/v1/wishlist/",
        json={"poi_name": "Colosseum", "city": "Rome", "country": "Italy", "category": "sightseeing"},
        headers=HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["poi_name"] == "Colosseum"


async def test_add_duplicate_wishlist(user_client):
    """Adding duplicate returns 409."""
    client, mock_db = user_client
    existing = _make_mock_wishlist_item()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=existing)
    mock_db.execute = AsyncMock(return_value=mock_result)

    response = await client.post(
        "/api/v1/wishlist/",
        json={"poi_name": "Colosseum", "city": "Rome"},
        headers=HEADERS,
    )
    assert response.status_code == 409


async def test_check_wishlisted_false(user_client):
    """Check returns false when not wishlisted."""
    client, _ = user_client
    response = await client.get(
        "/api/v1/wishlist/check",
        params={"poi_name": "Colosseum", "city": "Rome"},
        headers=HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_wishlisted"] is False
    assert data["item_id"] is None


async def test_check_wishlisted_true(user_client):
    """Check returns true when wishlisted."""
    client, mock_db = user_client
    item = _make_mock_wishlist_item()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=item)
    mock_db.execute = AsyncMock(return_value=mock_result)

    response = await client.get(
        "/api/v1/wishlist/check",
        params={"poi_name": "Colosseum", "city": "Rome"},
        headers=HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_wishlisted"] is True


async def test_remove_wishlist_not_found(user_client):
    """Removing non-existent item returns 404."""
    client, _ = user_client
    response = await client.delete(
        "/api/v1/wishlist/00000000-0000-0000-0000-000000000000",
        headers=HEADERS,
    )
    assert response.status_code == 404


async def test_wishlist_missing_header(user_client):
    """Wishlist fails without device ID."""
    client, _ = user_client
    response = await client.get("/api/v1/wishlist/")
    assert response.status_code == 422
