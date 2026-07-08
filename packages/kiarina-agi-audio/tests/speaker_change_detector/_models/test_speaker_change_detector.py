import numpy as np

from kiarina.agi.scd_model import scd_model_registry
from kiarina.agi.speaker_change_detector import (
    SpeakerChangeDetector,
    SpeakerChangeDetectorSettings,
)


async def test_speaker_change_detector() -> None:
    scd_model = scd_model_registry.create(
        "mock",
        speaker_probabilities=[
            [0.9, 0.1],
            [0.8, 0.2],
            [0.1, 0.1],
            [0.2, 0.8],
            [0.1, 0.9],
        ],
        frame_ms=100.0,
    )
    detector = SpeakerChangeDetector(
        scd_model,
        SpeakerChangeDetectorSettings(
            threshold=0.5,
            overlap_margin=0.05,
            min_change_ms=1,
            min_speech_ms=1,
        ),
    )

    speeches = await detector.detect(np.zeros(500, dtype=np.float32), 1000, 10.0)

    assert [(speech.speaker_index, speech.kind) for speech in speeches] == [
        (0, "speaker"),
        (1, "speaker"),
    ]
    assert speeches[0].start_timestamp == 10.0
    assert speeches[0].end_timestamp == 10.2
    assert speeches[1].start_timestamp == 10.2
    assert speeches[1].end_timestamp == 10.5


async def test_speaker_change_detector_emits_overlap() -> None:
    scd_model = scd_model_registry.create(
        "mock",
        speaker_probabilities=[
            [0.9, 0.1],
            [0.55, 0.52],
            [0.1, 0.9],
        ],
        frame_ms=100.0,
    )
    detector = SpeakerChangeDetector(
        scd_model,
        SpeakerChangeDetectorSettings(
            threshold=0.5,
            overlap_margin=0.05,
            min_change_ms=1,
            min_speech_ms=1,
        ),
    )

    speeches = await detector.detect(np.zeros(300, dtype=np.float32), 1000, 10.0)

    assert [(speech.speaker_index, speech.kind) for speech in speeches] == [
        (0, "speaker"),
        (-2, "unknown_overlap"),
        (1, "speaker"),
    ]


async def test_speaker_change_detector_all_silence() -> None:
    scd_model = scd_model_registry.create(
        "mock",
        speaker_probabilities=[
            [0.1, 0.1],
            [0.2, 0.2],
        ],
        frame_ms=100.0,
    )
    detector = SpeakerChangeDetector(
        scd_model,
        SpeakerChangeDetectorSettings(
            threshold=0.5,
            min_change_ms=1,
            min_speech_ms=1,
        ),
    )

    speeches = await detector.detect(np.zeros(200, dtype=np.float32), 1000, 10.0)

    assert len(speeches) == 1
    assert speeches[0].speaker_index == -1
    assert speeches[0].kind == "unknown_silence"


async def test_speaker_change_detector_downmixes() -> None:
    scd_model = scd_model_registry.create(
        "mock",
        speaker_probabilities=[[0.9]],
        frame_ms=100.0,
    )
    detector = SpeakerChangeDetector(scd_model, SpeakerChangeDetectorSettings())

    speeches = await detector.detect(np.ones((2, 100), dtype=np.float32), 1000, 10.0)

    assert len(speeches) == 1
    assert speeches[0].samples.ndim == 1
