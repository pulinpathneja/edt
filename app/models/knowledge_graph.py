"""
Knowledge Graph models for capturing relationships between POIs, neighborhoods, and cities.

This is an OPTIONAL enhancement that provides:
1. Rich relationship modeling between entities
2. Graph-based queries for "nearby", "similar", "on route to" queries
3. Better recommendation through relationship traversal

When to use Knowledge Graph vs Vector Search:
- Vector Search: "Find POIs matching this vibe/persona"
- Knowledge Graph: "What pairs well with Colosseum?" or "What's on the way?"
"""

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
    UniqueConstraint,
    Index,
    ARRAY,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class City(Base):
    """City-level information for multi-city support."""

    __tablename__ = "cities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False)
    country_code = Column(String(3))

    # Geographic
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    timezone = Column(String(50))

    # Travel context
    primary_language = Column(String(50))
    secondary_languages = Column(ARRAY(String))
    currency_code = Column(String(3))

    # Budget estimates (per day)
    avg_daily_budget_budget = Column(Numeric(10, 2))
    avg_daily_budget_midrange = Column(Numeric(10, 2))
    avg_daily_budget_luxury = Column(Numeric(10, 2))

    # Transportation
    has_metro = Column(Boolean, default=False)
    has_tram = Column(Boolean, default=False)
    has_bus = Column(Boolean, default=True)
    has_bike_share = Column(Boolean, default=False)
    is_walkable = Column(Boolean, default=True)
    uber_available = Column(Boolean, default=False)

    # Seasonality (array of month numbers)
    peak_season_months = Column(ARRAY(Integer))
    shoulder_season_months = Column(ARRAY(Integer))
    off_season_months = Column(ARRAY(Integer))

    # Quality scores (0-1)
    safety_score = Column(Numeric(3, 2))
    tourist_friendliness = Column(Numeric(3, 2))
    english_proficiency = Column(Numeric(3, 2))

    # Links
    wikipedia_url = Column(Text)
    official_tourism_url = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    neighborhoods = relationship("Neighborhood", back_populates="city", cascade="all, delete-orphan")


class Neighborhood(Base):
    """Neighborhood within a city."""

    __tablename__ = "neighborhoods"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    city_id = Column(UUID(as_uuid=True), ForeignKey("cities.id", ondelete="CASCADE"))
    name = Column(String(100), nullable=False)
    local_name = Column(String(100))

    # Geographic
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    boundary_geojson = Column(JSONB)

    # Character
    vibe_tags = Column(ARRAY(String))
    description = Column(Text)

    # Safety (0-1)
    safety_day = Column(Numeric(3, 2))
    safety_night = Column(Numeric(3, 2))

    # Accessibility (0-1)
    walkability_score = Column(Numeric(3, 2))
    transit_accessibility = Column(Numeric(3, 2))

    # Recommendations
    best_for = Column(ARRAY(String))
    avoid_for = Column(ARRAY(String))
    best_time_of_day = Column(String(20))

    # Density counts
    poi_density = Column(Integer)
    restaurant_density = Column(Integer)
    hotel_density = Column(Integer)

    # Relationships
    city = relationship("City", back_populates="neighborhoods")


class POIRelationship(Base):
    """
    Relationships between POIs for knowledge graph queries.

    Relationship Types:
    - NEAR_TO: Physical proximity (< 500m)
    - SAME_NEIGHBORHOOD: In the same area
    - SAME_THEME: Thematic connection (both Renaissance art)
    - PAIRS_WELL_WITH: Good to combine (museum + nearby cafe)
    - ALTERNATIVE_TO: Similar experience (if one is crowded)
    - PART_OF: Parent-child (Vatican Museums contains Sistine Chapel)
    - HISTORICAL_CONNECTION: Historical link
    - VIEW_OF: Has view of another POI
    - ON_ROUTE_TO: Commonly visited on way to
    """

    __tablename__ = "poi_relationships"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_poi_id = Column(UUID(as_uuid=True), ForeignKey("pois.id", ondelete="CASCADE"))
    target_poi_id = Column(UUID(as_uuid=True), ForeignKey("pois.id", ondelete="CASCADE"))
    relationship_type = Column(String(50), nullable=False)

    # Metadata
    strength = Column(Numeric(3, 2))  # 0-1 how strong the relationship
    bidirectional = Column(Boolean, default=False)
    description = Column(Text)

    # Distance-based relationships
    distance_meters = Column(Integer)
    walking_time_minutes = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("source_poi_id", "target_poi_id", "relationship_type", name="uq_poi_relationship"),
        Index("idx_poi_rel_source", "source_poi_id"),
        Index("idx_poi_rel_target", "target_poi_id"),
        Index("idx_poi_rel_type", "relationship_type"),
    )


class POICrowdPattern(Base):
    """Crowd patterns by day/hour for POIs."""

    __tablename__ = "poi_crowd_patterns"

    poi_id = Column(UUID(as_uuid=True), ForeignKey("pois.id", ondelete="CASCADE"), primary_key=True)
    day_of_week = Column(Integer, primary_key=True)  # 0=Monday, 6=Sunday
    hour_of_day = Column(Integer, primary_key=True)  # 0-23
    season = Column(String(20), primary_key=True)  # peak, shoulder, off

    crowd_level = Column(Numeric(3, 2))  # 0-1 normalized
    wait_time_minutes = Column(Integer)


class CityEvent(Base):
    """Events and festivals in cities."""

    __tablename__ = "city_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    city_id = Column(UUID(as_uuid=True), ForeignKey("cities.id", ondelete="CASCADE"))
    name = Column(String(200), nullable=False)
    event_type = Column(String(50))  # festival, holiday, sporting, cultural

    # Timing
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(String(50))  # annual, monthly, etc.

    # Impact
    crowd_impact = Column(Integer)  # 1-5
    price_impact = Column(Integer)  # 1-5

    # Relevance
    relevant_for = Column(ARRAY(String))

    description = Column(Text)


class NeighborhoodConnection(Base):
    """Connections between adjacent neighborhoods."""

    __tablename__ = "neighborhood_connections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    neighborhood_a_id = Column(UUID(as_uuid=True), ForeignKey("neighborhoods.id", ondelete="CASCADE"))
    neighborhood_b_id = Column(UUID(as_uuid=True), ForeignKey("neighborhoods.id", ondelete="CASCADE"))

    # Connection details
    is_walkable = Column(Boolean, default=True)
    walking_time_minutes = Column(Integer)
    transit_time_minutes = Column(Integer)
    transit_options = Column(ARRAY(String))  # ['metro', 'bus', 'tram']

    __table_args__ = (
        UniqueConstraint("neighborhood_a_id", "neighborhood_b_id", name="uq_neighborhood_connection"),
    )


class RestaurantDetail(Base):
    """Extended attributes for restaurant POIs."""

    __tablename__ = "restaurant_details"

    poi_id = Column(UUID(as_uuid=True), ForeignKey("pois.id", ondelete="CASCADE"), primary_key=True)

    # Cuisine
    cuisine_primary = Column(String(50))
    cuisine_secondary = Column(String(50))
    cuisine_tags = Column(ARRAY(String))

    # Dining style
    dining_style = Column(String(50))  # fine_dining, casual, fast_casual, street_food
    ambiance = Column(ARRAY(String))  # romantic, lively, quiet
    dress_code = Column(String(50))  # casual, smart_casual, formal

    # Reservations
    reservation_required = Column(Boolean)
    reservation_difficulty = Column(String(20))  # easy, moderate, hard, very_hard
    walk_ins_accepted = Column(Boolean)
    average_wait_minutes = Column(Integer)

    # Pricing
    price_range = Column(String(20))  # $, $$, $$$, $$$$
    avg_price_lunch = Column(Numeric(10, 2))
    avg_price_dinner = Column(Numeric(10, 2))
    tasting_menu_price = Column(Numeric(10, 2))

    # Features
    outdoor_seating = Column(Boolean)
    private_dining = Column(Boolean)
    bar_area = Column(Boolean)
    wine_list_notable = Column(Boolean)
    cocktail_menu = Column(Boolean)

    # Dietary
    vegetarian_options = Column(Boolean)
    vegan_options = Column(Boolean)
    gluten_free_options = Column(Boolean)
    halal_options = Column(Boolean)
    kosher_options = Column(Boolean)

    # Quality
    michelin_stars = Column(Integer)
    michelin_bib_gourmand = Column(Boolean)
    local_favorite = Column(Boolean)
    tourist_trap_risk = Column(Boolean)

    # Signature
    signature_dishes = Column(ARRAY(String))
    must_try_items = Column(ARRAY(String))


class POIAccessibility(Base):
    """Detailed accessibility information for POIs."""

    __tablename__ = "poi_accessibility"

    poi_id = Column(UUID(as_uuid=True), ForeignKey("pois.id", ondelete="CASCADE"), primary_key=True)

    # Mobility
    wheelchair_accessible = Column(Boolean)
    wheelchair_rental_available = Column(Boolean)
    elevator_available = Column(Boolean)
    ramps_available = Column(Boolean)
    accessible_parking = Column(Boolean)
    accessible_restroom = Column(Boolean)

    # Sensory
    braille_available = Column(Boolean)
    audio_description = Column(Boolean)
    sign_language_tours = Column(Boolean)
    large_print_available = Column(Boolean)
    quiet_hours_available = Column(Boolean)

    # Family
    stroller_accessible = Column(Boolean)
    stroller_rental = Column(Boolean)
    baby_changing_facilities = Column(Boolean)
    kids_menu_available = Column(Boolean)
    highchair_available = Column(Boolean)
    play_area = Column(Boolean)

    # Pet
    pets_allowed = Column(Boolean)
    pets_allowed_outside_only = Column(Boolean)
    water_bowls_available = Column(Boolean)

    # Notes
    accessibility_notes = Column(Text)
