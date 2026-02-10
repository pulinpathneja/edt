from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID


class PersonaTemplateCreate(BaseModel):
    """Create a new persona template."""

    name: str
    group_type: Optional[str] = None
    primary_vibes: Optional[List[str]] = None
    default_pacing: Optional[str] = None
    default_budget_level: Optional[int] = Field(default=None, ge=1, le=5)
    weight_config: Optional[Dict[str, Any]] = None
    filter_rules: Optional[Dict[str, Any]] = None


class PersonaTemplateResponse(PersonaTemplateCreate):
    """Response schema for persona template."""

    id: UUID

    class Config:
        from_attributes = True
