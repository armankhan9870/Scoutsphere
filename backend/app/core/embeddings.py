"""Embedding generator service producing 384-dimensional vectors for pgvector semantic search."""

import hashlib
import random
from typing import List

from app.core.config import settings
from app.core.logging import logger

try:
    from sentence_transformers import SentenceTransformer

    _local_model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
    logger.info("Loaded SentenceTransformers model: %s", settings.EMBEDDING_MODEL_NAME)
except Exception as e:
    logger.warning("SentenceTransformers local load fallback: %s", str(e))
    _local_model = None


def generate_embedding(text: str, dimension: int = 384) -> List[float]:
    """Generates a normalized L2 float vector for semantic search."""
    if _local_model is not None:
        try:
            vec = _local_model.encode(text, convert_to_numpy=True).tolist()
            norm = sum(x * x for x in vec) ** 0.5
            return [x / norm for x in vec] if norm > 0 else vec
        except Exception as e:
            logger.warning("Local embedding model encode failed: %s", str(e))

    # Deterministic fallback vector generation based on SHA256 text hash
    hash_obj = hashlib.sha256(text.encode("utf-8")).digest()
    rnd = random.Random(hash_obj)
    vec = [rnd.uniform(-1.0, 1.0) for _ in range(dimension)]
    norm = sum(x * x for x in vec) ** 0.5
    return [x / norm for x in vec]
