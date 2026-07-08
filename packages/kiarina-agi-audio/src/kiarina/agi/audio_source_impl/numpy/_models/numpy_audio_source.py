import asyncio
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import numpy as np

from kiarina.agi.audio_source import AudioChunk, BaseAudioSource
from kiarina.agi.audio_types import MultiChannelSamples

from .._settings import NumpyAudioSourceSettings


class NumpyAudioSource(BaseAudioSource):
    def __init__(self, settings: NumpyAudioSourceSettings) -> None:
        super().__init__()

        self.settings: NumpyAudioSourceSettings = settings
        self._samples: MultiChannelSamples | None = None
        self._start_timestamp: float | None = None

    @property
    def start_timestamp(self) -> float:
        if self._start_timestamp is None:
            raise AssertionError("start_timestamp is not set")

        return self._start_timestamp

    @asynccontextmanager
    async def _open(self, target: object | None) -> AsyncIterator[None]:
        if target is None:  # pragma: no cover
            raise TypeError("NumpyAudioSource target must be a numpy-compatible array")

        samples = np.asarray(target, dtype=np.float32)

        if samples.ndim == 1:
            samples = samples[np.newaxis, :]
        elif samples.ndim != 2:  # pragma: no cover
            raise ValueError(
                "NumpyAudioSource target must be 1D [Samples] or 2D [Channels, Samples]"
            )

        self._samples = samples
        self._start_timestamp = (
            self.settings.start_timestamp
            if self.settings.start_timestamp is not None
            else time.time()
        )

        try:
            yield
        finally:
            self._samples = None
            self._start_timestamp = None

    async def read(self, *stop_events: asyncio.Event) -> AsyncIterator[AudioChunk]:
        if self._samples is None:  # pragma: no cover
            raise RuntimeError("NumpyAudioSource must be opened with audio first")

        num_samples = self._samples.shape[1]

        for offset in range(0, num_samples, self.settings.chunk_size):
            if any(event.is_set() for event in stop_events):
                break

            yield AudioChunk(
                samples=self._samples[:, offset : offset + self.settings.chunk_size],
                sample_rate=self.settings.sample_rate,
                timestamp=self.start_timestamp + offset / self.settings.sample_rate,
            )
