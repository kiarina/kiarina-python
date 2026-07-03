import numpy as np

from kiarina.agi.embedding import l2_normalize


def test_l2_normalize() -> None:
    result = l2_normalize(np.array([3.0, 4.0], dtype=np.float32))

    assert result.dtype == np.float32
    assert np.allclose(result, [0.6, 0.8])


def test_keeps_zero_vector() -> None:
    result = l2_normalize(np.zeros(2, dtype=np.float32))

    assert np.allclose(result, [0.0, 0.0])
