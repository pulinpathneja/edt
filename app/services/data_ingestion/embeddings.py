from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.poi import POI
from app.core.embeddings import create_poi_description_embedding, generate_embeddings


class EmbeddingService:
    """Service for generating and updating POI embeddings."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_embeddings_for_poi(self, poi: POI) -> List[float]:
        """Generate embedding for a single POI."""
        embedding = create_poi_description_embedding(
            name=poi.name,
            description=poi.description or "",
            category=poi.category or "",
            subcategory=poi.subcategory or "",
            neighborhood=poi.neighborhood or "",
        )
        return embedding

    async def update_poi_embedding(self, poi_id: str, embedding: List[float]) -> None:
        """Update the embedding for a POI."""
        stmt = (
            update(POI)
            .where(POI.id == poi_id)
            .values(description_embedding=embedding)
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def generate_all_embeddings(self, batch_size: int = 50) -> int:
        """Generate embeddings for all POIs without embeddings."""
        # Get POIs without embeddings
        stmt = select(POI).where(POI.description_embedding.is_(None))
        result = await self.db.execute(stmt)
        pois = list(result.scalars().all())

        if not pois:
            return 0

        count = 0
        for i in range(0, len(pois), batch_size):
            batch = pois[i : i + batch_size]

            # Create texts for batch embedding
            texts = []
            for poi in batch:
                text = f"""
                {poi.name}: {poi.description or ''}
                Category: {poi.category or ''}, {poi.subcategory or ''}
                Location: {poi.neighborhood or ''}
                """
                texts.append(text)

            # Generate embeddings in batch
            embeddings = generate_embeddings(texts)

            # Update each POI
            for poi, embedding in zip(batch, embeddings):
                poi.description_embedding = embedding
                count += 1

            await self.db.commit()

        return count
