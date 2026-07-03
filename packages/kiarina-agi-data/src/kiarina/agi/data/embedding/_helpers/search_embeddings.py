from collections.abc import Iterable

import numpy as np

from .._schemas.embedding import Embedding
from .._schemas.embedding_search_result import EmbeddingSearchResult
from .calc_cosine_similarity import calc_cosine_similarity


def search_embeddings(
    query: Embedding | np.ndarray,
    candidates: Iterable[Embedding],
    *,
    top_k: int = 10,
    min_score: float | None = None,
) -> list[EmbeddingSearchResult]:
    if top_k <= 0:
        return []

    results: list[EmbeddingSearchResult] = []

    for candidate in candidates:
        if isinstance(query, Embedding) and query.space_id != candidate.space_id:
            continue

        score = calc_cosine_similarity(query, candidate)

        if min_score is not None and score < min_score:
            continue

        results.append(EmbeddingSearchResult(embedding=candidate, score=score))

    return sorted(results, key=lambda result: result.score, reverse=True)[:top_k]
