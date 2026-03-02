import uuid
from datetime import datetime, date
from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    Date,
    DateTime,
    ForeignKey,
    Index,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class DeviceSession(Base):
    """Anonymous device session for identity without login."""

    __tablename__ = "device_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(String(64), unique=True, nullable=False, index=True)
    platform = Column(String(20))  # ios, android, web
    app_version = Column(String(20))
    last_seen_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    drafts = relationship("TripDraft", back_populates="session", cascade="all, delete-orphan")
    wishlist_items = relationship("WishlistItem", back_populates="session", cascade="all, delete-orphan")


class TripDraft(Base):
    """Auto-saved trip planning draft for resume capability."""

    __tablename__ = "trip_drafts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(
        String(64),
        ForeignKey("device_sessions.device_id", ondelete="CASCADE"),
        nullable=False,
    )
    status = Column(String(20), default="active")  # active, completed, abandoned

    # Wizard progress
    current_step = Column(Integer, default=0)

    # Country selection
    country_id = Column(String(50))
    country_name = Column(String(100))

    # Dates
    start_date = Column(Date)
    end_date = Column(Date)

    # Preferences
    group_type = Column(String(30))
    group_size = Column(Integer)
    vibes = Column(JSON)  # List of vibe strings
    budget_level = Column(Integer)
    pacing = Column(String(20))

    # Allocation (selected city allocation option)
    selected_allocation = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    session = relationship("DeviceSession", back_populates="drafts")

    __table_args__ = (
        Index("ix_trip_drafts_device_status", "device_id", "status"),
    )


class WishlistItem(Base):
    """User-bookmarked POI with denormalized data."""

    __tablename__ = "wishlist_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(
        String(64),
        ForeignKey("device_sessions.device_id", ondelete="CASCADE"),
        nullable=False,
    )

    # Denormalized POI data (no FK to pois since itinerary-planner returns sample data)
    poi_name = Column(String(255), nullable=False)
    city = Column(String(100))
    country = Column(String(100))
    category = Column(String(50))
    image_url = Column(Text)
    description = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("DeviceSession", back_populates="wishlist_items")

    __table_args__ = (
        Index("ix_wishlist_device_poi_city", "device_id", "poi_name", "city"),
    )
