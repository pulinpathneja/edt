import uuid
from sqlalchemy import Column, String, Integer, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.core.database import Base


class PersonaTemplate(Base):
    """Persona templates for different traveler types."""

    __tablename__ = "persona_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)  # "Family with Young Kids", "Honeymoon Couple"

    # Default weights for this persona
    group_type = Column(String(50))  # family, couple, solo, friends, etc.
    primary_vibes = Column(ARRAY(String))  # array of dominant vibes

    # Default constraints
    default_pacing = Column(String(20))  # slow, moderate, fast
    default_budget_level = Column(Integer)  # 1-5

    # Scoring weights (how much each score matters)
    weight_config = Column(JSONB)  # flexible weights for scoring algorithm

    # Filtering rules
    filter_rules = Column(JSONB)  # hard constraints (e.g., must be kid-friendly)
