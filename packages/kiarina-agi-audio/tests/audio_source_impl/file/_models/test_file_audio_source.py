import numpy as np

from kiarina.agi.audio_source_impl.file import (
    FileAudioSource,
    FileAudioSourceSettings,
)
from kiarina.agi.audio_source_impl.file._models.file_audio_source import (
    _convert_channels,
    _resample,
)


async def test_file_audio_source(speech_audio_file_path: str) -> None:
    audio_source = FileAudioSource(FileAudioSourceSettings(start_timestamp=100.0))
    print(f"__str__: {audio_source}")

    async with audio_source.open(speech_audio_file_path):
        chunks = [chunk async for chunk in audio_source.read()]

    assert len(chunks) > 0
    assert chunks[0].samples.ndim == 2
    assert chunks[0].sample_rate > 0
    assert chunks[0].timestamp == 100.0

    if len(chunks) > 1:
        assert (
            chunks[1].timestamp
            == 100.0 + chunks[0].samples.shape[1] / chunks[0].sample_rate
        )


async def test_converts_sample_rate_and_channels(speech_audio_file_path: str) -> None:
    audio_source = FileAudioSource(
        FileAudioSourceSettings(
            chunk_size=256,
            sample_rate=8000,
            channels=1,
            start_timestamp=0.0,
        )
    )

    async with audio_source.open(speech_audio_file_path):
        chunks = [chunk async for chunk in audio_source.read()]

    assert len(chunks) > 0
    assert chunks[0].samples.shape == (1, 256)
    assert chunks[0].sample_rate == 8000
    assert chunks[0].timestamp == 0.0

    if len(chunks) > 1:
        assert (
            chunks[1].timestamp
            == 0.0 + chunks[0].samples.shape[1] / chunks[0].sample_rate
        )


def test_convert_channels_to_mono() -> None:
    samples = _convert_channels(
        np.asarray(
            [
                [1.0, 3.0],
                [3.0, 5.0],
            ],
            dtype=np.float32,
        ),
        1,
    )

    assert samples.shape == (1, 2)
    np.testing.assert_allclose(samples, [[2.0, 4.0]])


def test_convert_channels_repeats_mono() -> None:
    samples = _convert_channels(np.asarray([[1.0, 2.0]], dtype=np.float32), 2)

    assert samples.shape == (2, 2)
    np.testing.assert_allclose(samples, [[1.0, 2.0], [1.0, 2.0]])


def test_resample() -> None:
    samples = _resample(np.asarray([[0.0, 1.0, 2.0, 3.0]], dtype=np.float32), 4, 2)

    assert samples.shape == (1, 2)
    np.testing.assert_allclose(samples, [[0.0, 3.0]])
