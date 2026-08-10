import numpy as np
import pytest

from kiarina.agi.audio_tagging_provider import (
    AudioTagPrediction,
    BaseAudioTaggingProvider,
)
from kiarina.agi.audio_types import MonoSamples
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext


class ExampleAudioTaggingProvider(BaseAudioTaggingProvider):
    def __init__(self) -> None:
        super().__init__()
        self.samples: MonoSamples | None = None

    async def _predict(
        self,
        samples: MonoSamples,
        sample_rate: int,
        *,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> list[AudioTagPrediction]:
        self.samples = samples
        return [
            AudioTagPrediction(label="Bark", score=0.7),
            AudioTagPrediction(label="Meow", score=0.2),
        ]


async def test_base_audio_tagging_provider(run_context: RunContext) -> None:
    provider = ExampleAudioTaggingProvider()
    provider.name = "example"

    print(f"__str__: {provider!s}")
    print(f"name: {provider.name}")

    result = await provider.predict(np.zeros(1600), 16000, run_context=run_context)

    assert [p.label for p in result] == ["Bark", "Meow"]
    assert [p.score for p in result] == [0.7, 0.2]


async def test_accepts_stereo(run_context: RunContext) -> None:
    provider = ExampleAudioTaggingProvider()

    stereo = np.array(
        [
            [1.0, 2.0, 3.0],
            [3.0, 4.0, 5.0],
        ],
        dtype=np.float32,
    )

    result = await provider.predict(stereo, 16000, run_context=run_context)

    assert [p.label for p in result] == ["Bark", "Meow"]
    assert provider.samples is not None
    assert provider.samples.ndim == 1
    assert np.allclose(provider.samples, [2.0, 3.0, 4.0])


async def test_rejects_invalid_shape(run_context: RunContext) -> None:
    provider = ExampleAudioTaggingProvider()

    with pytest.raises(ValueError, match="samples must be 1D or 2D"):
        await provider.predict(np.zeros((1, 2, 3)), 16000, run_context=run_context)


async def test_supplies_null_cost_recorder(run_context: RunContext) -> None:
    captured: dict[str, CostRecorder] = {}

    class CapturingAudioTaggingProvider(BaseAudioTaggingProvider):
        async def _predict(
            self,
            samples: MonoSamples,
            sample_rate: int,
            *,
            cost_recorder: CostRecorder,
            run_context: RunContext,
        ) -> list[AudioTagPrediction]:
            captured["cost_recorder"] = cost_recorder
            return []

    provider = CapturingAudioTaggingProvider()
    provider.name = "capturing"

    await provider.predict(np.zeros(1600), 16000, run_context=run_context)

    assert captured["cost_recorder"] is not None
