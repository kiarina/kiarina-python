import numpy as np
import pytest

from kiarina.agi.asr_provider_impl.google import (
    GoogleASRProvider,
    GoogleASRProviderSettings,
)
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext


def test_init_and_properties() -> None:
    settings = GoogleASRProviderSettings()
    provider = GoogleASRProvider(settings)

    print(str(provider))
    print(f"client: {provider.client}")


@pytest.mark.costly
async def test_speech_to_text(
    cost_recorder: CostRecorder,
    run_context: RunContext,
    audio_samples: tuple[np.ndarray, int],
) -> None:
    settings = GoogleASRProviderSettings()
    provider = GoogleASRProvider(settings)
    samples, sample_rate = audio_samples

    text = await provider.speech_to_text(
        samples,
        sample_rate,
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    print("---- ASR Result ----")
    print(f"text:\n{text}")
    print("cost_record:")
    for record in cost_recorder.records:
        print(f" - {record}")

    assert len(text) > 0
    assert cost_recorder.total_microdollars > 0


@pytest.mark.costly
async def test_speech_to_text_with_extra_properties(
    cost_recorder: CostRecorder,
    run_context: RunContext,
    multi_speaker_audio_samples: tuple[np.ndarray, int],
) -> None:
    settings = GoogleASRProviderSettings(
        speakers={
            "speaker_1": "Woman",
            "speaker_2": "Man",
        },
        extra_segment_properties={
            "language": {
                "type": "string",
                "description": "The primary language of the segment",
            },
            "language_code": {
                "type": "string",
                "description": "ISO language code (e.g., 'en', 'ja')",
            },
            "emotion": {
                "type": "string",
                "enum": ["happy", "sad", "angry", "neutral"],
                "description": "The primary emotion of the speaker in this segment. You MUST choose exactly one of the following: happy, sad, angry, neutral.",
            },
        },
    )
    provider = GoogleASRProvider(settings)
    samples, sample_rate = multi_speaker_audio_samples

    segments = await provider.speech_to_segments(
        samples,
        sample_rate,
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    print("---- ASR Result with Extra Properties ----")
    print("segments:")
    for segment in segments:
        print(f"  - speaker: {segment.metadata.get('speaker_name')}")
        print(f"    text: {segment.text}")
        print(f"    metadata: {segment.metadata}")
    print("cost_record:")
    for record in cost_recorder.records:
        print(f" - {record}")

    assert len(segments) > 0
    assert cost_recorder.total_microdollars > 0

    # Check that metadata contains extra properties
    for segment in segments:
        assert "language" in segment.metadata
        assert "language_code" in segment.metadata
        assert "emotion" in segment.metadata
        assert segment.metadata["emotion"] in ["happy", "sad", "angry", "neutral"]
