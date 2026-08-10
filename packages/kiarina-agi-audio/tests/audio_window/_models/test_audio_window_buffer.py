import numpy as np
import pytest

from kiarina.agi.audio_window import AudioWindowBuffer


def test_audio_window_buffer_accept_emits_full_windows() -> None:
    buffer = AudioWindowBuffer(window_seconds=0.5)

    windows = buffer.accept(
        np.arange(12, dtype=np.float32),
        sample_rate=10,
        timestamp=100.0,
    )

    assert len(windows) == 2
    np.testing.assert_array_equal(windows[0].samples, np.arange(5, dtype=np.float32))
    assert windows[0].sample_rate == 10
    assert windows[0].start_timestamp == 100.0
    assert windows[0].end_timestamp == 100.5
    np.testing.assert_array_equal(
        windows[1].samples, np.arange(5, 10, dtype=np.float32)
    )
    assert windows[1].start_timestamp == 100.5
    assert windows[1].end_timestamp == 101.0


def test_audio_window_buffer_accept_emits_fixed_sample_windows() -> None:
    buffer = AudioWindowBuffer(window_samples=4)

    windows = buffer.accept(
        np.arange(10, dtype=np.float32),
        sample_rate=10,
        timestamp=100.0,
    )

    assert len(windows) == 2
    np.testing.assert_array_equal(windows[0].samples, np.arange(4, dtype=np.float32))
    assert windows[0].start_timestamp == 100.0
    assert windows[0].end_timestamp == pytest.approx(100.4)
    np.testing.assert_array_equal(windows[1].samples, np.arange(4, 8, dtype=np.float32))
    assert windows[1].start_timestamp == pytest.approx(100.4)
    assert windows[1].end_timestamp == pytest.approx(100.8)


def test_audio_window_buffer_flush_emits_remaining_samples() -> None:
    buffer = AudioWindowBuffer(window_seconds=0.5)

    windows = buffer.accept(
        np.arange(3, dtype=np.float32),
        sample_rate=10,
        timestamp=100.0,
    )

    assert windows == []

    windows = buffer.flush()

    assert len(windows) == 1
    np.testing.assert_array_equal(windows[0].samples, np.arange(3, dtype=np.float32))
    assert windows[0].start_timestamp == 100.0
    assert windows[0].end_timestamp == 100.3


def test_audio_window_buffer_preserves_channel_dimension() -> None:
    buffer = AudioWindowBuffer(window_seconds=0.5)
    samples = np.arange(12, dtype=np.float32).reshape(2, 6)

    windows = buffer.accept(samples, sample_rate=10, timestamp=100.0)

    assert len(windows) == 1
    np.testing.assert_array_equal(windows[0].samples, samples[:, :5])

    windows = buffer.flush()

    assert len(windows) == 1
    np.testing.assert_array_equal(windows[0].samples, samples[:, 5:])


def test_audio_window_buffer_rejects_sample_rate_change() -> None:
    buffer = AudioWindowBuffer(window_seconds=0.5)
    buffer.accept(np.arange(3, dtype=np.float32), sample_rate=10, timestamp=100.0)

    with pytest.raises(ValueError, match="stable sample_rate"):
        buffer.accept(np.arange(3, dtype=np.float32), sample_rate=20, timestamp=100.3)


def test_audio_window_buffer_rejects_non_positive_window_seconds() -> None:
    with pytest.raises(ValueError, match="greater than 0"):
        AudioWindowBuffer(window_seconds=0)


def test_audio_window_buffer_rejects_non_positive_window_samples() -> None:
    with pytest.raises(ValueError, match="greater than or equal to 1"):
        AudioWindowBuffer(window_samples=0)


def test_audio_window_buffer_rejects_ambiguous_window_size() -> None:
    with pytest.raises(ValueError, match="Exactly one"):
        AudioWindowBuffer()

    with pytest.raises(ValueError, match="Exactly one"):
        AudioWindowBuffer(window_seconds=0.5, window_samples=5)
