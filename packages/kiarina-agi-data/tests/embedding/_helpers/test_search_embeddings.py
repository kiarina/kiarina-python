import numpy as np

from kiarina.agi.embedding import Embedding, search_embeddings


def _embedding(
    vector: list[float],
    *,
    id: str,
    space_id: str = "text:example",
) -> Embedding:
    return Embedding(id=id, kind="text", space_id=space_id, vector=vector)


def test_returns_top_k_by_score() -> None:
    query = _embedding([1.0, 0.0], id="query")
    candidates = [
        _embedding([0.0, 1.0], id="orthogonal"),
        _embedding([1.0, 0.0], id="same"),
        _embedding([0.5, 0.5], id="middle"),
    ]

    results = search_embeddings(query, candidates, top_k=2)

    assert [result.embedding.id for result in results] == ["same", "middle"]
    assert np.isclose(results[0].score, 1.0)


def test_filters_by_min_score() -> None:
    query = _embedding([1.0, 0.0], id="query")
    candidates = [
        _embedding([1.0, 0.0], id="same"),
        _embedding([0.0, 1.0], id="orthogonal"),
    ]

    results = search_embeddings(query, candidates, min_score=0.5)

    assert [result.embedding.id for result in results] == ["same"]


def test_skips_different_spaces_for_embedding_query() -> None:
    query = _embedding([1.0, 0.0], id="query", space_id="text:example")
    candidates = [
        _embedding([1.0, 0.0], id="same-space", space_id="text:example"),
        _embedding([1.0, 0.0], id="other-space", space_id="text:other"),
    ]

    results = search_embeddings(query, candidates)

    assert [result.embedding.id for result in results] == ["same-space"]


def test_ndarray_query_searches_all_spaces() -> None:
    query = np.array([1.0, 0.0], dtype=np.float32)
    candidates = [
        _embedding([1.0, 0.0], id="text", space_id="text:example"),
        _embedding([1.0, 0.0], id="image", space_id="image:example"),
    ]

    results = search_embeddings(query, candidates)

    assert [result.embedding.id for result in results] == ["text", "image"]


def test_top_k_zero() -> None:
    query = _embedding([1.0, 0.0], id="query")
    candidates = [_embedding([1.0, 0.0], id="same")]

    assert search_embeddings(query, candidates, top_k=0) == []
