from abc import ABC, abstractmethod
from pathlib import Path

import numpy as np

from kiarina.agi.audio_types import AudioSamples, MonoSamples
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.cost_recorder_impl.null import NullCostRecorder
from kiarina.agi.local_repository import create_local_repository
from kiarina.agi.run_context import RunContext

from .._schemas.asr_segment import ASRSegment
from .._types.asr_provider import ASRProvider
from .._types.asr_provider_name import ASRProviderName
from .._utils.encode_wav import encode_wav
from .._utils.write_wav import write_wav


class BaseASRProvider(ASRProvider, ABC):
    def __init__(self) -> None:
        self._name: ASRProviderName | None = None

    @property
    def name(self) -> ASRProviderName:
        if self._name is None:  # pragma: no cover
            raise ValueError("ASRProvider name is not set.")

        return self._name

    @name.setter
    def name(self, value: ASRProviderName) -> None:
        self._name = value

    async def speech_to_text(
        self,
        samples: AudioSamples,
        sample_rate: int,
        *,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> str:
        samples = _to_mono(samples)

        if not cost_recorder:
            cost_recorder = NullCostRecorder()

        run_context = run_context.with_metadata(asr_provider=f"{self}")

        return await self._speech_to_text(
            samples,
            sample_rate,
            cost_recorder=cost_recorder,
            run_context=run_context,
        )

    async def speech_to_segments(
        self,
        samples: AudioSamples,
        sample_rate: int,
        *,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> list[ASRSegment]:
        samples = _to_mono(samples)

        if not cost_recorder:
            cost_recorder = NullCostRecorder()

        run_context = run_context.with_metadata(asr_provider=f"{self}")

        return await self._speech_to_segments(
            samples,
            sample_rate,
            cost_recorder=cost_recorder,
            run_context=run_context,
        )

    @abstractmethod
    async def _speech_to_text(
        self,
        samples: MonoSamples,
        sample_rate: int,
        *,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> str: ...

    @abstractmethod
    async def _speech_to_segments(
        self,
        samples: MonoSamples,
        sample_rate: int,
        *,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> list[ASRSegment]: ...

    def _encode_wav(self, samples: MonoSamples, sample_rate: int) -> bytes:
        return encode_wav(samples, sample_rate)

    def _write_samples_to_cache(
        self,
        samples: MonoSamples,
        sample_rate: int,
        run_context: RunContext,
        *,
        sub_dir_path: str = "asr",
    ) -> str:
        file_path = create_local_repository(run_context).generate_time_based_file_path(
            "input.wav",
            sub_dir_path=sub_dir_path,
            area="cache",
        )

        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        write_wav(file_path, samples, sample_rate)
        return file_path

    def __str__(self) -> str:
        return self.__class__.__name__


def _to_mono(samples: AudioSamples) -> MonoSamples:
    samples = np.asarray(samples)

    if samples.ndim == 1:
        return samples

    if samples.ndim == 2:
        return samples[0] if samples.shape[0] == 1 else samples.mean(axis=0)

    raise ValueError(
        f"samples must be 1D or 2D [Channels, Samples], got shape {samples.shape}."
    )
