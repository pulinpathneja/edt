from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db
from app.models.persona import PersonaTemplate
from app.schemas.persona import PersonaTemplateCreate, PersonaTemplateResponse
from app.core.config import GROUP_TYPES, VIBE_CATEGORIES

router = APIRouter()


@router.get("/config")
async def get_persona_config():
    """Get available persona configuration options."""
    return {
        "group_types": GROUP_TYPES,
        "vibe_categories": VIBE_CATEGORIES,
        "pacing_options": ["slow", "moderate", "fast"],
        "budget_levels": list(range(1, 6)),
    }


@router.get("/", response_model=List[PersonaTemplateResponse])
async def list_persona_templates(
    db: AsyncSession = Depends(get_db),
):
    """List all persona templates."""
    stmt = select(PersonaTemplate)
    result = await db.execute(stmt)
    templates = result.scalars().all()
    return templates


@router.get("/{template_id}", response_model=PersonaTemplateResponse)
async def get_persona_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a single persona template by ID."""
    stmt = select(PersonaTemplate).where(PersonaTemplate.id == template_id)
    result = await db.execute(stmt)
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(status_code=404, detail="Persona template not found")

    return template


@router.post("/", response_model=PersonaTemplateResponse)
async def create_persona_template(
    template_data: PersonaTemplateCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new persona template."""
    template = PersonaTemplate(**template_data.model_dump())
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template


@router.put("/{template_id}", response_model=PersonaTemplateResponse)
async def update_persona_template(
    template_id: UUID,
    template_data: PersonaTemplateCreate,
    db: AsyncSession = Depends(get_db),
):
    """Update a persona template."""
    stmt = select(PersonaTemplate).where(PersonaTemplate.id == template_id)
    result = await db.execute(stmt)
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(status_code=404, detail="Persona template not found")

    for field, value in template_data.model_dump().items():
        setattr(template, field, value)

    await db.commit()
    await db.refresh(template)
    return template


@router.delete("/{template_id}")
async def delete_persona_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete a persona template."""
    stmt = select(PersonaTemplate).where(PersonaTemplate.id == template_id)
    result = await db.execute(stmt)
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(status_code=404, detail="Persona template not found")

    await db.delete(template)
    await db.commit()

    return {"status": "deleted", "id": str(template_id)}
