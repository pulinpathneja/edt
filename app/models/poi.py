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
    ForeignKey,
    CheckConstraint,
    ARRAY,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from app.core.database import Base
from app.core.config import get_settings

settings = get_settings()


class POI(Base):
    """Points of Interest table."""

    __tablename__ = "pois"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)

    # Location
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    address = Column(Text)
    neighborhood = Column(String(100))
    city = Column(String(100), default="Rome")
    country = Column(String(100), default="Italy")

    # Classification
    category = Column(String(50))  # restaurant, attraction, activity, etc.
    subcategory = Column(String(50))  # museum, beach, hiking, fine_dining, etc.

    # Timing
    typical_duration_minutes = Column(Integer)
    best_time_of_day = Column(String(20))  # morning, afternoon, evening, night, any
    best_days = Column(ARRAY(Text))  # weekday, weekend, specific days
    seasonal_availability = Column(ARRAY(Text))  # spring, summer, fall, winter, all

    # Cost
    cost_level = Column(Integer, CheckConstraint("cost_level BETWEEN 1 AND 5"))
    avg_cost_per_person = Column(Numeric(10, 2))
    cost_currency = Column(String(3), default="EUR")

    # Embedding for RAG (384 dimensions for BGE-small-en-v1.5)
    description_embedding = Column(Vector(settings.embedding_dimension))

    # Metadata
    source = Column(String(50))  # overture, google, manual
    source_id = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    persona_scores = relationship(
        "POIPersonaScores", back_populates="poi", uselist=False, cascade="all, delete-orphan"
    )
    attributes = relationship(
        "POIAttributes", back_populates="poi", uselist=False, cascade="all, delete-orphan"
    )


class POIPersonaScores(Base):
    """Persona match scores for each POI."""

    __tablename__ = "poi_persona_scores"

    poi_id = Column(UUID(as_uuid=True), ForeignKey("pois.id", ondelete="CASCADE"), primary_key=True)

    # Group Type Scores (0.0 to 1.0)
    score_family = Column(Numeric(3, 2), default=0.5)
    score_kids = Column(Numeric(3, 2), default=0.5)
    score_couple = Column(Numeric(3, 2), default=0.5)
    score_honeymoon = Column(Numeric(3, 2), default=0.5)
    score_solo = Column(Numeric(3, 2), default=0.5)
    score_friends = Column(Numeric(3, 2), default=0.5)
    score_seniors = Column(Numeric(3, 2), default=0.5)
    score_business = Column(Numeric(3, 2), default=0.5)

    # Vibe Scores (0.0 to 1.0)
    score_adventure = Column(Numeric(3, 2), default=0.5)
    score_relaxation = Column(Numeric(3, 2), default=0.5)
    score_cultural = Column(Numeric(3, 2), default=0.5)
    score_foodie = Column(Numeric(3, 2), default=0.5)
    score_nightlife = Column(Numeric(3, 2), default=0.5)
    score_nature = Column(Numeric(3, 2), default=0.5)
    score_shopping = Column(Numeric(3, 2), default=0.5)
    score_photography = Column(Numeric(3, 2), default=0.5)
    score_wellness = Column(Numeric(3, 2), default=0.5)
    score_romantic = Column(Numeric(3, 2), default=0.5)

    # Practical Scores
    score_accessibility = Column(Numeric(3, 2), default=0.5)
    score_indoor = Column(Numeric(3, 2), default=0.5)

    # Season Scores (0.0 to 1.0) - how suitable for each season
    score_spring = Column(Numeric(3, 2), default=0.7)
    score_summer = Column(Numeric(3, 2), default=0.7)
    score_fall = Column(Numeric(3, 2), default=0.7)
    score_winter = Column(Numeric(3, 2), default=0.7)

    # Relationship
    poi = relationship("POI", back_populates="persona_scores")


class POIAttributes(Base):
    """Additional attributes for POI filtering."""

    __tablename__ = "poi_attributes"

    poi_id = Column(UUID(as_uuid=True), ForeignKey("pois.id", ondelete="CASCADE"), primary_key=True)

    # Practical Info
    is_kid_friendly = Column(Boolean, default=True)
    is_pet_friendly = Column(Boolean, default=False)
    is_wheelchair_accessible = Column(Boolean, default=False)
    requires_reservation = Column(Boolean, default=False)
    requires_advance_booking_days = Column(Integer, default=0)

    # Physical
    is_indoor = Column(Boolean)
    is_outdoor = Column(Boolean)
    physical_intensity = Column(
        Integer, CheckConstraint("physical_intensity BETWEEN 1 AND 5")
    )  # 1=sedentary, 5=strenuous

    # Crowd & Experience
    typical_crowd_level = Column(
        Integer, CheckConstraint("typical_crowd_level BETWEEN 1 AND 5")
    )
    is_hidden_gem = Column(Boolean, default=False)
    is_must_see = Column(Boolean, default=False)
    instagram_worthy = Column(Boolean, default=False)

    # Weather Sensitivity
    weather_dependent = Column(Boolean, default=False)  # Experience affected by weather
    rain_suitable = Column(Boolean, default=True)  # Can visit when raining
    heat_sensitive = Column(Boolean, default=False)  # Avoid on very hot days
    cold_sensitive = Column(Boolean, default=False)  # Avoid on very cold days

    # Time Sensitivity
    best_in_morning = Column(Boolean, default=False)  # Best visited early
    best_in_evening = Column(Boolean, default=False)  # Best at sunset/night
    sunset_worthy = Column(Boolean, default=False)  # Worth visiting at golden hour
    night_visit_possible = Column(Boolean, default=False)  # Open/accessible at night

    # Seasonal Notes
    peak_season_crowd_multiplier = Column(Numeric(3, 2), default=1.0)  # 1.5 = 50% more crowded
    off_season_discount = Column(Boolean, default=False)  # Cheaper off-season
    seasonal_closure = Column(String(100))  # e.g., "Closed November-March"

    # Relationship
    poi = relationship("POI", back_populates="attributes")
