import numpy as np

from kiarina.agi.audio_types import AudioSamples

from .._schemas.audio_window import AudioWindow


class AudioWindowBuffer:
    def __init__(
        self,
        *,
        window_samples: int | None = None,
        window_seconds: float | None = None,
    ) -> None:
        if (window_samples is None) == (window_seconds is None):
            raise ValueError(
                "Exactly one of window_seconds or window_samples must be set."
            )

        if window_samples is not None and window_samples < 1:
            raise ValueError("window_samples must be greater than or equal to 1.")

        if window_seconds is not None and window_seconds <= 0:
            raise ValueError("window_seconds must be greater than 0.")

        self.requested_window_samples: int | None = window_samples
        self.requested_window_seconds: float | None = window_seconds
        self.sample_rate: int | None = None
        self.window_samples: int | None = None
        self.buffer: AudioSamples | None = None
        self.buffer_start_timestamp: float | None = None

    def accept(
        self,
        samples: AudioSamples,
        *,
        sample_rate: int,
        timestamp: float,
    ) -> list[AudioWindow]:
        self._ensure_sample_rate(sample_rate)

        if self.buffer is None or _sample_count(self.buffer) == 0:
            self.buffer = samples
            self.buffer_start_timestamp = timestamp

        else:
            self.buffer = np.concatenate([self.buffer, samples], axis=-1)

        return self._drain(full_windows_only=True)

    def flush(self) -> list[AudioWindow]:
        return self._drain(full_windows_only=False)

    def _ensure_sample_rate(self, sample_rate: int) -> None:
        if self.sample_rate is None:
            self.sample_rate = sample_rate

            if self.requested_window_samples is not None:
                self.window_samples = self.requested_window_samples
            elif self.requested_window_seconds is not None:
                self.window_samples = max(
                    1, round(self.requested_window_seconds * sample_rate)
                )

            return

        if self.sample_rate != sample_rate:
            raise ValueError(
                "AudioWindowBuffer expects a stable sample_rate, "
                f"got {self.sample_rate} then {sample_rate}."
            )

    def _drain(self, *, full_windows_only: bool) -> list[AudioWindow]:
        windows: list[AudioWindow] = []

        if self.buffer is None or self.buffer_start_timestamp is None:
            return windows

        if self.sample_rate is None or self.window_samples is None:
            return windows

        while _sample_count(self.buffer) > 0:
            if full_windows_only and _sample_count(self.buffer) < self.window_samples:
                return windows

            end_sample = min(self.window_samples, _sample_count(self.buffer))
            samples = _slice_samples(self.buffer, end_sample)
            start_timestamp = self.buffer_start_timestamp
            end_timestamp = start_timestamp + _sample_count(samples) / self.sample_rate

            windows.append(
                AudioWindow(
                    samples=samples,
                    sample_rate=self.sample_rate,
                    start_timestamp=start_timestamp,
                    end_timestamp=end_timestamp,
                )
            )

            self.buffer = _drop_samples(self.buffer, end_sample)
            self.buffer_start_timestamp = end_timestamp

        return windows


def _sample_count(samples: AudioSamples) -> int:
    return int(samples.shape[-1])


def _slice_samples(samples: AudioSamples, end_sample: int) -> AudioSamples:
    return samples[..., :end_sample]


def _drop_samples(samples: AudioSamples, end_sample: int) -> AudioSamples:
    return samples[..., end_sample:]
