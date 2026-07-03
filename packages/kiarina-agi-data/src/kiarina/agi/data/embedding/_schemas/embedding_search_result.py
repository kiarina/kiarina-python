from pydantic import BaseModel

from .embedding import Embedding


class EmbeddingSearchResult(BaseModel):
    embedding: Embedding
    score: float
