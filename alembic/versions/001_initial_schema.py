"""Initial schema with all tables

Revision ID: 001_initial
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable extensions
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # Create pois table
    op.create_table(
        "pois",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("latitude", sa.Numeric(10, 8)),
        sa.Column("longitude", sa.Numeric(11, 8)),
        sa.Column("address", sa.Text),
        sa.Column("neighborhood", sa.String(100)),
        sa.Column("city", sa.String(100), server_default="Rome"),
        sa.Column("country", sa.String(100), server_default="Italy"),
        sa.Column("category", sa.String(50)),
        sa.Column("subcategory", sa.String(50)),
        sa.Column("typical_duration_minutes", sa.Integer),
        sa.Column("best_time_of_day", sa.String(20)),
        sa.Column("best_days", postgresql.ARRAY(sa.Text)),
        sa.Column("seasonal_availability", postgresql.ARRAY(sa.Text)),
        sa.Column("cost_level", sa.Integer),
        sa.Column("avg_cost_per_person", sa.Numeric(10, 2)),
        sa.Column("cost_currency", sa.String(3), server_default="EUR"),
        sa.Column("description_embedding", Vector(384)),  # BGE-small-en-v1.5 dimension
        sa.Column("source", sa.String(50)),
        sa.Column("source_id", sa.String(255)),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime, server_default=sa.text("NOW()")),
        sa.CheckConstraint("cost_level BETWEEN 1 AND 5", name="check_cost_level"),
    )

    # Create index for vector similarity search
    op.execute(
        "CREATE INDEX idx_pois_embedding ON pois USING ivfflat (description_embedding vector_cosine_ops) WITH (lists = 100)"
    )

    # Create poi_persona_scores table
    op.create_table(
        "poi_persona_scores",
        sa.Column("poi_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("pois.id", ondelete="CASCADE"), primary_key=True),
        # Group Type Scores
        sa.Column("score_family", sa.Numeric(3, 2), server_default="0.5"),
        sa.Column("score_kids", sa.Numeric(3, 2), server_default="0.5"),
        sa.Column("score_couple", sa.Numeric(3, 2), server_default="0.5"),
        sa.Column("score_honeymoon", sa.Numeric(3, 2), server_default="0.5"),
        sa.Column("score_solo", sa.Numeric(3, 2), server_default="0.5"),
        sa.Column("score_friends", sa.Numeric(3, 2), server_default="0.5"),
        sa.Column("score_seniors", sa.Numeric(3, 2), server_default="0.5"),
        sa.Column("score_business", sa.Numeric(3, 2), server_default="0.5"),
        # Vibe Scores
        sa.Column("score_adventure", sa.Numeric(3, 2), server_default="0.5"),
        sa.Column("score_relaxation", sa.Numeric(3, 2), server_default="0.5"),
        sa.Column("score_cultural", sa.Numeric(3, 2), server_default="0.5"),
        sa.Column("score_foodie", sa.Numeric(3, 2), server_default="0.5"),
        sa.Column("score_nightlife", sa.Numeric(3, 2), server_default="0.5"),
        sa.Column("score_nature", sa.Numeric(3, 2), server_default="0.5"),
        sa.Column("score_shopping", sa.Numeric(3, 2), server_default="0.5"),
        sa.Column("score_photography", sa.Numeric(3, 2), server_default="0.5"),
        sa.Column("score_wellness", sa.Numeric(3, 2), server_default="0.5"),
        sa.Column("score_romantic", sa.Numeric(3, 2), server_default="0.5"),
        # Practical Scores
        sa.Column("score_accessibility", sa.Numeric(3, 2), server_default="0.5"),
        sa.Column("score_indoor", sa.Numeric(3, 2), server_default="0.5"),
    )

    # Create poi_attributes table
    op.create_table(
        "poi_attributes",
        sa.Column("poi_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("pois.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("is_kid_friendly", sa.Boolean, server_default="true"),
        sa.Column("is_pet_friendly", sa.Boolean, server_default="false"),
        sa.Column("is_wheelchair_accessible", sa.Boolean, server_default="false"),
        sa.Column("requires_reservation", sa.Boolean, server_default="false"),
        sa.Column("requires_advance_booking_days", sa.Integer, server_default="0"),
        sa.Column("is_indoor", sa.Boolean),
        sa.Column("is_outdoor", sa.Boolean),
        sa.Column("physical_intensity", sa.Integer),
        sa.Column("typical_crowd_level", sa.Integer),
        sa.Column("is_hidden_gem", sa.Boolean, server_default="false"),
        sa.Column("is_must_see", sa.Boolean, server_default="false"),
        sa.Column("instagram_worthy", sa.Boolean, server_default="false"),
        sa.CheckConstraint("physical_intensity BETWEEN 1 AND 5", name="check_physical_intensity"),
        sa.CheckConstraint("typical_crowd_level BETWEEN 1 AND 5", name="check_crowd_level"),
    )

    # Create persona_templates table
    op.create_table(
        "persona_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("group_type", sa.String(50)),
        sa.Column("primary_vibes", postgresql.ARRAY(sa.String)),
        sa.Column("default_pacing", sa.String(20)),
        sa.Column("default_budget_level", sa.Integer),
        sa.Column("weight_config", postgresql.JSONB),
        sa.Column("filter_rules", postgresql.JSONB),
    )

    # Create trip_requests table
    op.create_table(
        "trip_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True)),
        sa.Column("destination_city", sa.String(100)),
        sa.Column("start_date", sa.Date),
        sa.Column("end_date", sa.Date),
        sa.Column("group_type", sa.String(50)),
        sa.Column("group_size", sa.Integer),
        sa.Column("has_kids", sa.Boolean, server_default="false"),
        sa.Column("kids_ages", postgresql.ARRAY(sa.Integer)),
        sa.Column("has_seniors", sa.Boolean, server_default="false"),
        sa.Column("vibes", postgresql.ARRAY(sa.String)),
        sa.Column("budget_level", sa.Integer),
        sa.Column("daily_budget", sa.Numeric(10, 2)),
        sa.Column("pacing", sa.String(20)),
        sa.Column("mobility_constraints", postgresql.ARRAY(sa.String)),
        sa.Column("dietary_restrictions", postgresql.ARRAY(sa.String)),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("NOW()")),
    )

    # Create itineraries table
    op.create_table(
        "itineraries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("trip_request_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("trip_requests.id", ondelete="CASCADE")),
        sa.Column("total_estimated_cost", sa.Numeric(10, 2)),
        sa.Column("generation_method", sa.String(50)),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("NOW()")),
    )

    # Create itinerary_days table
    op.create_table(
        "itinerary_days",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("itinerary_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("itineraries.id", ondelete="CASCADE")),
        sa.Column("day_number", sa.Integer),
        sa.Column("date", sa.Date),
        sa.Column("theme", sa.String(100)),
        sa.Column("estimated_cost", sa.Numeric(10, 2)),
        sa.Column("pacing_score", sa.Numeric(3, 2)),
    )

    # Create itinerary_items table
    op.create_table(
        "itinerary_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("itinerary_day_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("itinerary_days.id", ondelete="CASCADE")),
        sa.Column("poi_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("pois.id", ondelete="SET NULL")),
        sa.Column("sequence_order", sa.Integer),
        sa.Column("start_time", sa.Time),
        sa.Column("end_time", sa.Time),
        sa.Column("selection_reason", sa.Text),
        sa.Column("persona_match_score", sa.Numeric(3, 2)),
        sa.Column("travel_time_from_previous", sa.Integer),
        sa.Column("travel_mode", sa.String(20)),
    )

    # Create indexes
    op.create_index("idx_pois_city", "pois", ["city"])
    op.create_index("idx_pois_category", "pois", ["category"])
    op.create_index("idx_pois_neighborhood", "pois", ["neighborhood"])
    op.create_index("idx_trip_requests_user_id", "trip_requests", ["user_id"])
    op.create_index("idx_itinerary_days_itinerary_id", "itinerary_days", ["itinerary_id"])
    op.create_index("idx_itinerary_items_day_id", "itinerary_items", ["itinerary_day_id"])


def downgrade() -> None:
    op.drop_table("itinerary_items")
    op.drop_table("itinerary_days")
    op.drop_table("itineraries")
    op.drop_table("trip_requests")
    op.drop_table("persona_templates")
    op.drop_table("poi_attributes")
    op.drop_table("poi_persona_scores")
    op.execute("DROP INDEX IF EXISTS idx_pois_embedding")
    op.drop_table("pois")
