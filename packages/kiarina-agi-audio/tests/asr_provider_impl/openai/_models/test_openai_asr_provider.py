from pathlib import Path

import numpy as np
import pytest

from kiarina.agi.asr_provider_impl.openai import (
    OpenAIASRProvider,
    OpenAIASRProviderSettings,
)
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext


def test_init_and_properties() -> None:
    settings = OpenAIASRProviderSettings()
    provider = OpenAIASRProvider(settings)

    print(str(provider))
    print(f"openai_settings: {provider.openai_settings}")
    print(f"client: {provider.client}")


@pytest.mark.costly
async def test_speech_to_text(
    cost_recorder: CostRecorder,
    run_context: RunContext,
    audio_samples: tuple[np.ndarray, int],
) -> None:
    settings = OpenAIASRProviderSettings()
    provider = OpenAIASRProvider(settings)
    samples, sample_rate = audio_samples

    text = await provider.speech_to_text(
        samples,
        sample_rate,
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    print("---- ASR Result ----")
    print(f"text: {text}")
    print("cost_record:")
    for record in cost_recorder.records:
        print(f" - {record}")

    assert len(text) > 0
    assert cost_recorder.total_microdollars > 0


@pytest.mark.costly
async def test_speech_to_text_with_diarization(
    cost_recorder: CostRecorder,
    run_context: RunContext,
    test_data_dir: Path,
    multi_speaker_audio_samples: tuple[np.ndarray, int],
) -> None:
    settings = OpenAIASRProviderSettings(
        segments_model_name="gpt-4o-transcribe-diarize",
        speakers={
            "speaker_1": str(test_data_dir / "asr" / "reference_voice_1.mp3"),
            "speaker_2": str(test_data_dir / "asr" / "reference_voice_2.mp3"),
        },
    )
    provider = OpenAIASRProvider(settings)
    samples, sample_rate = multi_speaker_audio_samples

    segments = await provider.speech_to_segments(
        samples,
        sample_rate,
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    print("---- ASR with Diarization Result ----")
    print(f"segments: {segments}")
    print("cost_record:")
    for record in cost_recorder.records:
        print(f" - {record}")

    assert len(segments) > 0
    assert cost_recorder.total_microdollars > 0
