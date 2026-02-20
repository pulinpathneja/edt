from sentence_transformers import SentenceTransformer
from functools import lru_cache
import numpy as np
from typing import Dict, List, Optional, Union

from app.core.config import get_settings

settings = get_settings()


@lru_cache()
def get_embedding_model() -> SentenceTransformer:
    """Load the embedding model (cached for efficiency)."""
    return SentenceTransformer(settings.embedding_model)


def generate_embedding(text: str) -> List[float]:
    """Generate embedding for a single text."""
    model = get_embedding_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for multiple texts."""
    model = get_embedding_model()
    embeddings = model.encode(texts, normalize_embeddings=True)
    return embeddings.tolist()


def cosine_similarity(vec1: Union[List[float], np.ndarray], vec2: Union[List[float], np.ndarray]) -> float:
    """Calculate cosine similarity between two vectors."""
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))


def create_poi_query_embedding(
    destination: str,
    group_type: str,
    vibes: List[str],
    pacing: str,
) -> List[float]:
    """Create a query embedding for POI retrieval."""
    query = f"""
    {destination} trip for {group_type}
    vibes: {', '.join(vibes)}
    looking for {pacing} paced activities
    """
    return generate_embedding(query)


def create_poi_description_embedding(
    name: str,
    description: str,
    category: str,
    subcategory: str,
    neighborhood: str,
) -> List[float]:
    """Create an embedding for a POI based on its details."""
    text = f"""
    {name}: {description}
    Category: {category}, {subcategory}
    Location: {neighborhood}
    """
    return generate_embedding(text)


def create_enriched_poi_embedding_text(
    name: str,
    description: str,
    category: str,
    subcategory: str,
    neighborhood: str,
    city: str = "",
    persona_scores: Optional[Dict[str, float]] = None,
    attributes: Optional[Dict[str, bool]] = None,
) -> str:
    """
    Create a rich text representation of a POI for embedding.

    Includes strong persona vibes and attribute tags so the embedding
    captures semantic intent better (e.g., "romantic", "hidden gem").
    """
    parts = [name]

    # Use description only if it's meaningful (not just "Name - category in City")
    if description and description != f"{name} - {category} in {city}":
        parts.append(description)

    if category:
        parts.append(f"Type: {category}")
    if subcategory and subcategory != category:
        parts.append(f"Style: {subcategory}")
    if neighborhood:
        parts.append(f"Area: {neighborhood}")

    # Add strong persona signals
    if persona_scores:
        strong_vibes = []
        for vibe in [
            "romantic", "cultural", "foodie", "adventure", "relaxation",
            "nature", "nightlife", "photography", "wellness", "shopping",
        ]:
            score = persona_scores.get(f"score_{vibe}", 0.5)
            if isinstance(score, (int, float)) and score >= 0.75:
                strong_vibes.append(vibe)
        if strong_vibes:
            parts.append(f"Known for: {', '.join(strong_vibes)}")

    # Add attribute tags
    if attributes:
        tags = []
        if attributes.get("is_hidden_gem"):
            tags.append("hidden gem")
        if attributes.get("is_must_see"):
            tags.append("must-see")
        if attributes.get("instagram_worthy"):
            tags.append("photogenic")
        if attributes.get("is_kid_friendly"):
            tags.append("family-friendly")
        if tags:
            parts.append(f"Tags: {', '.join(tags)}")

    return ". ".join(parts)


def create_enriched_poi_embedding(
    name: str,
    description: str,
    category: str,
    subcategory: str,
    neighborhood: str,
    city: str = "",
    persona_scores: Optional[Dict[str, float]] = None,
    attributes: Optional[Dict[str, bool]] = None,
) -> List[float]:
    """Create an enriched embedding for a POI."""
    text = create_enriched_poi_embedding_text(
        name=name,
        description=description,
        category=category,
        subcategory=subcategory,
        neighborhood=neighborhood,
        city=city,
        persona_scores=persona_scores,
        attributes=attributes,
    )
    return generate_embedding(text)
