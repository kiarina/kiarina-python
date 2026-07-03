from pydantic import BaseModel

from .._models.embedding import Embedding


class EmbeddingSearchResult(BaseModel):
    embedding: Embedding
    score: float
