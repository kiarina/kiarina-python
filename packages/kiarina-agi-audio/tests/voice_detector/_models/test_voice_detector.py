import numpy as np
import pytest

from kiarina.agi.vad_model import vad_model_registry
from kiarina.agi.voice_detector import (
    VoiceDetector,
    VoiceDetectorSettings,
)


async def test_voice_detector() -> None:
    vad_model = vad_model_registry.create(
        "mock",
        sample_rate=1000,
        speech_probabilities=[0.0, 0.9, 0.9, 0.0, 0.0, 0.9],
    )
    detector = VoiceDetector(
        vad_model,
        VoiceDetectorSettings(
            threshold=0.5,
            min_silence_ms=200,
            voice_pad_ms=100,
        ),
    )

    samples = np.zeros(100, dtype=np.float32)

    result = await detector.detect(samples, 1000, 10.0)  # prob 0.0
    assert result.is_voice is False
    assert result.probability == 0.0
    assert result.voice is None

    result = await detector.detect(samples, 1000, 10.1)  # prob 0.9
    assert result.is_voice is True
    assert result.probability == 0.9
    assert result.voice is None

    assert (await detector.detect(samples, 1000, 10.2)).voice is None  # prob 0.9
    assert (await detector.detect(samples, 1000, 10.3)).voice is None  # prob 0.0

    result = await detector.detect(samples, 1000, 10.4)  # prob 0.0 -> emit
    voice = result.voice

    assert voice is not None
    assert voice.sample_rate == 1000
    assert voice.samples.ndim == 1
    assert voice.start_timestamp == 10.0
    assert voice.end_timestamp == 10.4

    assert detector.flush() is None
    assert (await detector.detect(samples, 1000, 10.5)).voice is None  # prob 0.9
    flushed = detector.flush()
    assert flushed is not None
    assert flushed.start_timestamp == 10.5
    assert flushed.end_timestamp == 10.6


async def test_voice_detector_provider_rejects_sample_rate() -> None:
    vad_model = vad_model_registry.create("mock", sample_rate=16000)
    detector = VoiceDetector(vad_model, VoiceDetectorSettings())

    with pytest.raises(ValueError, match="MockVADProvider expects sample_rate 16000"):
        await detector.detect(np.zeros(100), 1000, 0.0)


async def test_voice_detector_downmixes_and_exposes_in_voice() -> None:
    vad_model = vad_model_registry.create(
        "mock",
        sample_rate=1000,
        speech_probabilities=[0.0, 0.9],
    )
    detector = VoiceDetector(vad_model, VoiceDetectorSettings(threshold=0.5))

    assert detector.in_voice is False

    # 2D [Channels, Samples] input is downmixed to mono internally.
    stereo = np.ones((2, 100), dtype=np.float32)

    result = await detector.detect(stereo, 1000, 0.0)
    assert result.is_voice is False
    assert detector.in_voice is False

    result = await detector.detect(stereo, 1000, 0.1)
    assert result.is_voice is True
    assert detector.in_voice is True
