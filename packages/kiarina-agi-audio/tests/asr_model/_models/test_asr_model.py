from collections.abc import Iterator

import numpy as np
import pytest

from kiarina.agi.asr_model import ASRModel, ASRModelConfig
from kiarina.agi.asr_provider import (
    ASRSegment,
    BaseASRProvider,
    settings_manager,
)
from kiarina.agi.audio_types import MonoSamples
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext


class ASRProvider(BaseASRProvider):
    def __init__(self, *args: object) -> None: ...

    async def _speech_to_text(
        self,
        samples: MonoSamples,
        sample_rate: int,
        *,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> str:
        return f"{len(samples)} samples at {sample_rate} Hz"

    async def _speech_to_segments(
        self,
        samples: MonoSamples,
        sample_rate: int,
        *,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> list[ASRSegment]:
        return []


@pytest.fixture(autouse=True)
def setup() -> Iterator[None]:
    settings_manager.cli_args = {"customs": {"my_provider": __name__ + ":ASRProvider"}}
    yield
    settings_manager.cli_args = {}


async def test_asr_model(run_context: RunContext) -> None:
    asr_model = ASRModel("my_model", ASRModelConfig(provider_name="my_provider"))

    result = await asr_model.speech_to_text(
        np.asarray([0.0, 0.5, -0.5], dtype=np.float32),
        16_000,
        run_context=run_context,
    )

    assert result == "3 samples at 16000 Hz"
