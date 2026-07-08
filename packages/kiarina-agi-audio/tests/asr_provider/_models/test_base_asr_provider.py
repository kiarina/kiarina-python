import numpy as np
import pytest

from kiarina.agi.asr_provider import ASRSegment, BaseASRProvider
from kiarina.agi.audio_types import MonoSamples
from kiarina.agi.cost_record import CostRecord
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext


class ASRProvider(BaseASRProvider):
    def __init__(self, *args: object) -> None:
        super().__init__()
        self.seen_samples: MonoSamples | None = None
        self.seen_sample_rate: int | None = None

    async def _speech_to_text(
        self,
        samples: MonoSamples,
        sample_rate: int,
        *,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> str:
        self.seen_samples = samples
        self.seen_sample_rate = sample_rate
        cost_recorder.add(
            CostRecord(
                microdollars=1,
                kind="asr",
                source="my_asr_provider",
            )
        )
        return f"{len(samples)} samples"

    async def _speech_to_segments(
        self,
        samples: MonoSamples,
        sample_rate: int,
        *,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> list[ASRSegment]:
        self.seen_samples = samples
        self.seen_sample_rate = sample_rate
        return [
            ASRSegment(
                text=f"{len(samples)} samples",
                start_timestamp=0.0,
                end_timestamp=1.0,
            )
        ]


async def test_base_asr_provider(
    cost_recorder: CostRecorder, run_context: RunContext
) -> None:
    provider = ASRProvider()
    samples = np.asarray([0.0, 0.5, -0.5], dtype=np.float32)

    result = await provider.speech_to_text(
        samples,
        16_000,
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    assert result == "3 samples"
    assert provider.seen_sample_rate == 16_000
    assert provider.seen_samples is not None
    assert np.array_equal(provider.seen_samples, samples)
    assert cost_recorder.total_microdollars == 1


async def test_base_asr_provider_converts_to_mono(
    cost_recorder: CostRecorder, run_context: RunContext
) -> None:
    provider = ASRProvider()
    samples = np.asarray(
        [
            [0.0, 0.5, -0.5],
            [1.0, 0.5, 0.0],
        ],
        dtype=np.float32,
    )

    result = await provider.speech_to_text(
        samples,
        16_000,
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    assert result == "3 samples"
    assert provider.seen_samples is not None
    assert np.allclose(provider.seen_samples, np.asarray([0.5, 0.5, -0.25]))


async def test_base_asr_provider_speech_to_segments(
    cost_recorder: CostRecorder, run_context: RunContext
) -> None:
    provider = ASRProvider()

    segments = await provider.speech_to_segments(
        np.asarray([0.0, 0.5, -0.5], dtype=np.float32),
        16_000,
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    assert segments[0].text == "3 samples"


async def test_base_asr_provider_rejects_invalid_shape(
    cost_recorder: CostRecorder, run_context: RunContext
) -> None:
    provider = ASRProvider()

    with pytest.raises(ValueError, match="samples must be 1D or 2D"):
        await provider.speech_to_text(
            np.zeros((1, 2, 3), dtype=np.float32),
            16_000,
            cost_recorder=cost_recorder,
            run_context=run_context,
        )
