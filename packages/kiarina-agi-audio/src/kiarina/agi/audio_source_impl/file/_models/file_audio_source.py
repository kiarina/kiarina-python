import asyncio
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

import numpy as np

from kiarina.agi.audio_source import AudioChunk, BaseAudioSource
from kiarina.agi.audio_types import MultiChannelSamples

from .._settings import FileAudioSourceSettings

try:
    import soundfile as sf  # type: ignore
except ImportError as exc:
    raise ImportError(
        "soundfile is required to use FileAudioSource. "
        "Install it with: pip install 'kiarina-agi-audio[audio-source-file]'"
    ) from exc


class FileAudioSource(BaseAudioSource):
    def __init__(self, settings: FileAudioSourceSettings) -> None:
        super().__init__()

        self.settings: FileAudioSourceSettings = settings
        self._file_path: Path | None = None
        self._start_timestamp: float | None = None

    @property
    def file_path(self) -> Path:
        if self._file_path is None:
            raise AssertionError("file_path is not set")

        return self._file_path

    @property
    def start_timestamp(self) -> float:
        if self._start_timestamp is None:
            raise AssertionError("start_timestamp is not set")

        return self._start_timestamp

    @asynccontextmanager
    async def _open(self, target: object | None) -> AsyncIterator[None]:
        if not isinstance(target, str | Path):
            raise TypeError("FileAudioSource target must be a str or Path")

        self._file_path = Path(target).expanduser()
        self._start_timestamp = (
            self.settings.start_timestamp
            if self.settings.start_timestamp is not None
            else time.time()
        )

        try:
            yield
        finally:
            self._file_path = None
            self._start_timestamp = None

    async def read(self, *stop_events: asyncio.Event) -> AsyncIterator[AudioChunk]:
        with sf.SoundFile(self.file_path) as audio_file:
            source_sample_rate = audio_file.samplerate
            sample_rate = (
                self.settings.sample_rate
                if self.settings.sample_rate is not None
                else source_sample_rate
            )

            if sample_rate < 1:
                raise ValueError("sample_rate must be greater than or equal to 1")

            if self.settings.chunk_size < 1:
                raise ValueError("chunk_size must be greater than or equal to 1")

            source_chunk_size = _get_source_chunk_size(
                self.settings.chunk_size,
                source_sample_rate,
                sample_rate,
            )

            offset = 0
            pending_samples: MultiChannelSamples | None = None

            while not any(event.is_set() for event in stop_events):
                samples = audio_file.read(
                    frames=source_chunk_size,
                    dtype="float32",
                    always_2d=True,
                )

                if len(samples) == 0:
                    break

                # soundfile yields [Samples, Channels]; normalize to [Channels, Samples]
                samples = np.asarray(samples, dtype=np.float32).T
                samples = _convert_channels(samples, self.settings.channels)
                samples = _resample(samples, source_sample_rate, sample_rate).astype(
                    np.float32,
                    copy=False,
                )
                pending_samples = _append_samples(pending_samples, samples)

                while pending_samples.shape[1] >= self.settings.chunk_size and not any(
                    event.is_set() for event in stop_events
                ):
                    chunk_samples = pending_samples[:, : self.settings.chunk_size]
                    pending_samples = pending_samples[:, self.settings.chunk_size :]

                    yield AudioChunk(
                        samples=chunk_samples,
                        sample_rate=sample_rate,
                        timestamp=self.start_timestamp + offset / sample_rate,
                    )

                    offset += chunk_samples.shape[1]

            if (
                pending_samples is not None
                and pending_samples.shape[1] > 0
                and not any(event.is_set() for event in stop_events)
            ):
                yield AudioChunk(
                    samples=pending_samples,
                    sample_rate=sample_rate,
                    timestamp=self.start_timestamp + offset / sample_rate,
                )


def _convert_channels(
    samples: MultiChannelSamples, channels: int | None
) -> MultiChannelSamples:
    if channels is None or samples.shape[0] == channels:
        return samples

    if channels < 1:
        raise ValueError("channels must be greater than or equal to 1")

    if channels == 1:
        return samples.mean(axis=0, keepdims=True)

    if samples.shape[0] == 1:
        return np.repeat(samples, channels, axis=0)

    if samples.shape[0] > channels:
        return samples[:channels]

    repeats = int(np.ceil(channels / samples.shape[0]))
    return np.tile(samples, (repeats, 1))[:channels]


def _resample(
    samples: MultiChannelSamples,
    source_sample_rate: int,
    target_sample_rate: int,
) -> MultiChannelSamples:
    if source_sample_rate == target_sample_rate:
        return samples

    if target_sample_rate < 1:
        raise ValueError("sample_rate must be greater than or equal to 1")

    source_length = samples.shape[1]

    if source_length == 0:
        return samples

    source_duration = source_length / source_sample_rate
    target_length = max(1, round(source_duration * target_sample_rate))
    source_positions = np.linspace(0.0, source_length - 1, num=source_length)
    target_positions = np.linspace(0.0, source_length - 1, num=target_length)

    return np.vstack(
        [np.interp(target_positions, source_positions, channel) for channel in samples]
    )


def _get_source_chunk_size(
    output_chunk_size: int,
    source_sample_rate: int,
    target_sample_rate: int,
) -> int:
    return max(1, round(output_chunk_size * source_sample_rate / target_sample_rate))


def _append_samples(
    current: MultiChannelSamples | None,
    additional: MultiChannelSamples,
) -> MultiChannelSamples:
    if current is None:
        return additional

    if current.shape[1] == 0:
        return additional

    if additional.shape[1] == 0:
        return current

    return np.concatenate([current, additional], axis=1)
