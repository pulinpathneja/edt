"""
CityInsight model — stores scraped travel intelligence from Reddit,
TripAdvisor, and blog sources in the database for querying.
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Text,
    Float,
    DateTime,
    Index,
    ARRAY,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.core.database import Base


class CityInsight(Base):
    """A single piece of travel intelligence scraped for a city."""

    __tablename__ = "city_insights"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    city = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False, server_default="")
    source = Column(String(50), nullable=False)       # reddit | tripadvisor | blog
    category = Column(String(50), nullable=False, server_default="general")
    title = Column(Text, nullable=False, server_default="")
    content = Column(Text, nullable=False, server_default="")
    url = Column(Text)
    relevance_score = Column(Float, server_default="0")
    rating = Column(Float)                             # e.g. 4.5 (TripAdvisor)
    author = Column(String(200))
    source_date = Column(DateTime)                     # original post/article date
    metadata_ = Column("metadata", JSONB, server_default="{}")
    persona_tags = Column(ARRAY(String), server_default="{}")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_city_insights_city", "city"),
        Index("idx_city_insights_source", "source"),
        Index("idx_city_insights_category", "category"),
        Index("idx_city_insights_city_source", "city", "source"),
        Index("idx_city_insights_city_category", "city", "category"),
    )

    def __repr__(self) -> str:
        return f"<CityInsight {self.source}:{self.city} — {self.title[:50]}>"
