import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    Boolean,
    Numeric,
    DateTime,
    Date,
    Time,
    ForeignKey,
    ARRAY,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class TripRequest(Base):
    """User trip request input."""

    __tablename__ = "trip_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True))

    # Basic Info
    destination_city = Column(String(100))
    start_date = Column(Date)
    end_date = Column(Date)

    # Persona Selection
    group_type = Column(String(50))
    group_size = Column(Integer)
    has_kids = Column(Boolean, default=False)
    kids_ages = Column(ARRAY(Integer))
    has_seniors = Column(Boolean, default=False)

    # Preferences
    vibes = Column(ARRAY(String))  # selected vibes
    budget_level = Column(Integer)  # 1-5
    daily_budget = Column(Numeric(10, 2))
    pacing = Column(String(20))  # slow, moderate, fast

    # Constraints
    mobility_constraints = Column(ARRAY(String))
    dietary_restrictions = Column(ARRAY(String))

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    itineraries = relationship("Itinerary", back_populates="trip_request", cascade="all, delete-orphan")


class Itinerary(Base):
    """Generated itinerary."""

    __tablename__ = "itineraries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_request_id = Column(UUID(as_uuid=True), ForeignKey("trip_requests.id", ondelete="CASCADE"))

    # Metadata
    total_estimated_cost = Column(Numeric(10, 2))
    generation_method = Column(String(50))  # rag_v1, rag_v2, etc.

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    trip_request = relationship("TripRequest", back_populates="itineraries")
    days = relationship("ItineraryDay", back_populates="itinerary", cascade="all, delete-orphan")


class ItineraryDay(Base):
    """A single day in an itinerary."""

    __tablename__ = "itinerary_days"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    itinerary_id = Column(UUID(as_uuid=True), ForeignKey("itineraries.id", ondelete="CASCADE"))
    day_number = Column(Integer)
    date = Column(Date)
    theme = Column(String(100))  # "Beach & Relaxation", "Cultural Exploration"

    # Daily summary
    estimated_cost = Column(Numeric(10, 2))
    pacing_score = Column(Numeric(3, 2))  # actual pacing achieved

    # Relationships
    itinerary = relationship("Itinerary", back_populates="days")
    items = relationship("ItineraryItem", back_populates="day", cascade="all, delete-orphan")


class ItineraryItem(Base):
    """A single item (activity/meal) in an itinerary day."""

    __tablename__ = "itinerary_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    itinerary_day_id = Column(UUID(as_uuid=True), ForeignKey("itinerary_days.id", ondelete="CASCADE"))
    poi_id = Column(UUID(as_uuid=True), ForeignKey("pois.id", ondelete="SET NULL"))

    sequence_order = Column(Integer)
    start_time = Column(Time)
    end_time = Column(Time)

    # Why this was selected (explainability)
    selection_reason = Column(Text)
    persona_match_score = Column(Numeric(3, 2))

    # Logistics
    travel_time_from_previous = Column(Integer)  # minutes
    travel_mode = Column(String(20))  # walk, drive, transit

    # Relationships
    day = relationship("ItineraryDay", back_populates="items")
    poi = relationship("POI")
