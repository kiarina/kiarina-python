import numpy as np
import pytest

from kiarina.agi.embedding import Embedding, calc_cosine_similarity


def test_embeddings() -> None:
    x = Embedding(kind="text", space_id="text:example", vector=[3.0, 4.0])
    y = Embedding(kind="text", space_id="text:example", vector=[6.0, 8.0])

    assert np.isclose(calc_cosine_similarity(x, y), 1.0)


def test_rejects_different_spaces() -> None:
    x = Embedding(kind="text", space_id="text:example", vector=[1.0, 0.0])
    y = Embedding(kind="text", space_id="text:other", vector=[1.0, 0.0])

    with pytest.raises(
        ValueError,
        match="Cannot compare embeddings from different spaces",
    ):
        calc_cosine_similarity(x, y)


def test_arrays() -> None:
    x = np.array([1.0, 0.0], dtype=np.float32)
    y = np.array([0.0, 1.0], dtype=np.float32)

    assert np.isclose(calc_cosine_similarity(x, y), 0.0)


def test_allows_embedding_and_array() -> None:
    x = Embedding(kind="text", space_id="text:example", vector=[1.0, 0.0])
    y = np.array([1.0, 0.0], dtype=np.float32)

    assert np.isclose(calc_cosine_similarity(x, y), 1.0)


def test_shape_mismatch() -> None:
    x = np.array([1.0, 0.0], dtype=np.float32)
    y = np.array([1.0, 0.0, 0.0], dtype=np.float32)

    assert calc_cosine_similarity(x, y) == float("-inf")


def test_zero_vector() -> None:
    x = np.array([0.0, 0.0], dtype=np.float32)
    y = np.array([1.0, 0.0], dtype=np.float32)

    assert calc_cosine_similarity(x, y) == 0.0


def test_rejects_matrix() -> None:
    with pytest.raises(ValueError, match="Expected x to be a 1D vector"):
        calc_cosine_similarity(
            np.zeros((1, 2), dtype=np.float32),
            np.zeros(2, dtype=np.float32),
        )
