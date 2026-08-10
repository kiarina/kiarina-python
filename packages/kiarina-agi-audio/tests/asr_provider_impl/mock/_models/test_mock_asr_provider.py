import numpy as np

from kiarina.agi.asr_provider_impl.mock import (
    MockASRProvider,
    MockASRProviderSettings,
)
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext


def test_initialize_and_properties() -> None:
    settings = MockASRProviderSettings()
    provider = MockASRProvider(settings)

    print(str(provider))


async def test_speech_to_text(
    cost_recorder: CostRecorder, run_context: RunContext
) -> None:
    settings = MockASRProviderSettings()
    provider = MockASRProvider(settings)

    text = await provider.speech_to_text(
        np.asarray([0.0, 0.5, -0.5], dtype=np.float32),
        16_000,
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    assert text == settings.result_text

    segments = await provider.speech_to_segments(
        np.asarray([0.0, 0.5, -0.5], dtype=np.float32),
        16_000,
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    assert segments == settings.result_segments
