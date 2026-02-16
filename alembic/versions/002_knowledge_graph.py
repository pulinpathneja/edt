"""Knowledge Graph tables

Revision ID: 002_knowledge_graph
Revises: 001_initial
Create Date: 2024-01-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "002_knowledge_graph"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create cities table
    op.create_table(
        "cities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("country", sa.String(100), nullable=False),
        sa.Column("country_code", sa.String(3)),
        sa.Column("latitude", sa.Numeric(10, 8)),
        sa.Column("longitude", sa.Numeric(11, 8)),
        sa.Column("timezone", sa.String(50)),
        sa.Column("primary_language", sa.String(50)),
        sa.Column("secondary_languages", postgresql.ARRAY(sa.String)),
        sa.Column("currency_code", sa.String(3)),
        sa.Column("avg_daily_budget_budget", sa.Numeric(10, 2)),
        sa.Column("avg_daily_budget_midrange", sa.Numeric(10, 2)),
        sa.Column("avg_daily_budget_luxury", sa.Numeric(10, 2)),
        sa.Column("has_metro", sa.Boolean, server_default="false"),
        sa.Column("has_tram", sa.Boolean, server_default="false"),
        sa.Column("has_bus", sa.Boolean, server_default="true"),
        sa.Column("has_bike_share", sa.Boolean, server_default="false"),
        sa.Column("is_walkable", sa.Boolean, server_default="true"),
        sa.Column("uber_available", sa.Boolean, server_default="false"),
        sa.Column("peak_season_months", postgresql.ARRAY(sa.Integer)),
        sa.Column("shoulder_season_months", postgresql.ARRAY(sa.Integer)),
        sa.Column("off_season_months", postgresql.ARRAY(sa.Integer)),
        sa.Column("safety_score", sa.Numeric(3, 2)),
        sa.Column("tourist_friendliness", sa.Numeric(3, 2)),
        sa.Column("english_proficiency", sa.Numeric(3, 2)),
        sa.Column("wikipedia_url", sa.Text),
        sa.Column("official_tourism_url", sa.Text),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("NOW()")),
    )

    # Create neighborhoods table
    op.create_table(
        "neighborhoods",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("city_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cities.id", ondelete="CASCADE")),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("local_name", sa.String(100)),
        sa.Column("latitude", sa.Numeric(10, 8)),
        sa.Column("longitude", sa.Numeric(11, 8)),
        sa.Column("boundary_geojson", postgresql.JSONB),
        sa.Column("vibe_tags", postgresql.ARRAY(sa.String)),
        sa.Column("description", sa.Text),
        sa.Column("safety_day", sa.Numeric(3, 2)),
        sa.Column("safety_night", sa.Numeric(3, 2)),
        sa.Column("walkability_score", sa.Numeric(3, 2)),
        sa.Column("transit_accessibility", sa.Numeric(3, 2)),
        sa.Column("best_for", postgresql.ARRAY(sa.String)),
        sa.Column("avoid_for", postgresql.ARRAY(sa.String)),
        sa.Column("best_time_of_day", sa.String(20)),
        sa.Column("poi_density", sa.Integer),
        sa.Column("restaurant_density", sa.Integer),
        sa.Column("hotel_density", sa.Integer),
    )

    # Create poi_relationships table
    op.create_table(
        "poi_relationships",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("source_poi_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("pois.id", ondelete="CASCADE")),
        sa.Column("target_poi_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("pois.id", ondelete="CASCADE")),
        sa.Column("relationship_type", sa.String(50), nullable=False),
        sa.Column("strength", sa.Numeric(3, 2)),
        sa.Column("bidirectional", sa.Boolean, server_default="false"),
        sa.Column("description", sa.Text),
        sa.Column("distance_meters", sa.Integer),
        sa.Column("walking_time_minutes", sa.Integer),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("NOW()")),
        sa.UniqueConstraint("source_poi_id", "target_poi_id", "relationship_type", name="uq_poi_relationship"),
    )

    # Create poi_crowd_patterns table
    op.create_table(
        "poi_crowd_patterns",
        sa.Column("poi_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("pois.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("day_of_week", sa.Integer, primary_key=True),
        sa.Column("hour_of_day", sa.Integer, primary_key=True),
        sa.Column("season", sa.String(20), primary_key=True),
        sa.Column("crowd_level", sa.Numeric(3, 2)),
        sa.Column("wait_time_minutes", sa.Integer),
    )

    # Create city_events table
    op.create_table(
        "city_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("city_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cities.id", ondelete="CASCADE")),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("event_type", sa.String(50)),
        sa.Column("start_date", sa.DateTime),
        sa.Column("end_date", sa.DateTime),
        sa.Column("is_recurring", sa.Boolean, server_default="false"),
        sa.Column("recurrence_pattern", sa.String(50)),
        sa.Column("crowd_impact", sa.Integer),
        sa.Column("price_impact", sa.Integer),
        sa.Column("relevant_for", postgresql.ARRAY(sa.String)),
        sa.Column("description", sa.Text),
    )

    # Create neighborhood_connections table
    op.create_table(
        "neighborhood_connections",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("neighborhood_a_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("neighborhoods.id", ondelete="CASCADE")),
        sa.Column("neighborhood_b_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("neighborhoods.id", ondelete="CASCADE")),
        sa.Column("is_walkable", sa.Boolean, server_default="true"),
        sa.Column("walking_time_minutes", sa.Integer),
        sa.Column("transit_time_minutes", sa.Integer),
        sa.Column("transit_options", postgresql.ARRAY(sa.String)),
        sa.UniqueConstraint("neighborhood_a_id", "neighborhood_b_id", name="uq_neighborhood_connection"),
    )

    # Create restaurant_details table
    op.create_table(
        "restaurant_details",
        sa.Column("poi_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("pois.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("cuisine_primary", sa.String(50)),
        sa.Column("cuisine_secondary", sa.String(50)),
        sa.Column("cuisine_tags", postgresql.ARRAY(sa.String)),
        sa.Column("dining_style", sa.String(50)),
        sa.Column("ambiance", postgresql.ARRAY(sa.String)),
        sa.Column("dress_code", sa.String(50)),
        sa.Column("reservation_required", sa.Boolean),
        sa.Column("reservation_difficulty", sa.String(20)),
        sa.Column("walk_ins_accepted", sa.Boolean),
        sa.Column("average_wait_minutes", sa.Integer),
        sa.Column("price_range", sa.String(20)),
        sa.Column("avg_price_lunch", sa.Numeric(10, 2)),
        sa.Column("avg_price_dinner", sa.Numeric(10, 2)),
        sa.Column("tasting_menu_price", sa.Numeric(10, 2)),
        sa.Column("outdoor_seating", sa.Boolean),
        sa.Column("private_dining", sa.Boolean),
        sa.Column("bar_area", sa.Boolean),
        sa.Column("wine_list_notable", sa.Boolean),
        sa.Column("cocktail_menu", sa.Boolean),
        sa.Column("vegetarian_options", sa.Boolean),
        sa.Column("vegan_options", sa.Boolean),
        sa.Column("gluten_free_options", sa.Boolean),
        sa.Column("halal_options", sa.Boolean),
        sa.Column("kosher_options", sa.Boolean),
        sa.Column("michelin_stars", sa.Integer),
        sa.Column("michelin_bib_gourmand", sa.Boolean),
        sa.Column("local_favorite", sa.Boolean),
        sa.Column("tourist_trap_risk", sa.Boolean),
        sa.Column("signature_dishes", postgresql.ARRAY(sa.String)),
        sa.Column("must_try_items", postgresql.ARRAY(sa.String)),
    )

    # Create poi_accessibility table
    op.create_table(
        "poi_accessibility",
        sa.Column("poi_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("pois.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("wheelchair_accessible", sa.Boolean),
        sa.Column("wheelchair_rental_available", sa.Boolean),
        sa.Column("elevator_available", sa.Boolean),
        sa.Column("ramps_available", sa.Boolean),
        sa.Column("accessible_parking", sa.Boolean),
        sa.Column("accessible_restroom", sa.Boolean),
        sa.Column("braille_available", sa.Boolean),
        sa.Column("audio_description", sa.Boolean),
        sa.Column("sign_language_tours", sa.Boolean),
        sa.Column("large_print_available", sa.Boolean),
        sa.Column("quiet_hours_available", sa.Boolean),
        sa.Column("stroller_accessible", sa.Boolean),
        sa.Column("stroller_rental", sa.Boolean),
        sa.Column("baby_changing_facilities", sa.Boolean),
        sa.Column("kids_menu_available", sa.Boolean),
        sa.Column("highchair_available", sa.Boolean),
        sa.Column("play_area", sa.Boolean),
        sa.Column("pets_allowed", sa.Boolean),
        sa.Column("pets_allowed_outside_only", sa.Boolean),
        sa.Column("water_bowls_available", sa.Boolean),
        sa.Column("accessibility_notes", sa.Text),
    )

    # Create indexes
    op.create_index("idx_cities_country", "cities", ["country"])
    op.create_index("idx_cities_name", "cities", ["name"])
    op.create_index("idx_neighborhoods_city_id", "neighborhoods", ["city_id"])
    op.create_index("idx_poi_rel_source", "poi_relationships", ["source_poi_id"])
    op.create_index("idx_poi_rel_target", "poi_relationships", ["target_poi_id"])
    op.create_index("idx_poi_rel_type", "poi_relationships", ["relationship_type"])
    op.create_index("idx_city_events_city_id", "city_events", ["city_id"])


def downgrade() -> None:
    op.drop_table("poi_accessibility")
    op.drop_table("restaurant_details")
    op.drop_table("neighborhood_connections")
    op.drop_table("city_events")
    op.drop_table("poi_crowd_patterns")
    op.drop_table("poi_relationships")
    op.drop_table("neighborhoods")
    op.drop_table("cities")
