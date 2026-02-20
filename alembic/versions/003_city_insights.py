"""City Insights table

Revision ID: 003_city_insights
Revises: 002_knowledge_graph
Create Date: 2024-01-20 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "003_city_insights"
down_revision: Union[str, None] = "002_knowledge_graph"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "city_insights",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("city", sa.String(100), nullable=False),
        sa.Column("country", sa.String(100), nullable=False, server_default=""),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("category", sa.String(50), nullable=False, server_default="general"),
        sa.Column("title", sa.Text, nullable=False, server_default=""),
        sa.Column("content", sa.Text, nullable=False, server_default=""),
        sa.Column("url", sa.Text),
        sa.Column("relevance_score", sa.Float, server_default="0"),
        sa.Column("rating", sa.Float),
        sa.Column("author", sa.String(200)),
        sa.Column("source_date", sa.DateTime),
        sa.Column("metadata", postgresql.JSONB, server_default="{}"),
        sa.Column("persona_tags", postgresql.ARRAY(sa.String), server_default="{}"),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime, server_default=sa.text("NOW()"), nullable=False),
    )

    # Indexes for common query patterns
    op.create_index("idx_city_insights_city", "city_insights", ["city"])
    op.create_index("idx_city_insights_source", "city_insights", ["source"])
    op.create_index("idx_city_insights_category", "city_insights", ["category"])
    op.create_index("idx_city_insights_city_source", "city_insights", ["city", "source"])
    op.create_index("idx_city_insights_city_category", "city_insights", ["city", "category"])


def downgrade() -> None:
    op.drop_table("city_insights")
