import numpy as np
import pytest

from kiarina.agi.asr_model import speech_to_text
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext


@pytest.mark.costly
async def test_speech_to_text(
    asr_model_name: str,
    cost_recorder: CostRecorder,
    run_context: RunContext,
    audio_samples: tuple[np.ndarray, int],
) -> None:
    samples, sample_rate = audio_samples

    text = await speech_to_text(
        samples,
        sample_rate,
        asr_options={"asr_model": asr_model_name},
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    print("---- ASR Result ----")
    print(f"text: {text}")
    print("cost_record:")
    for record in cost_recorder.records:
        print(f" - {record}")

    assert len(text) > 0
