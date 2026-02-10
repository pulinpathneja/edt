from sentence_transformers import SentenceTransformer
from functools import lru_cache
import numpy as np
from typing import List, Union

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
