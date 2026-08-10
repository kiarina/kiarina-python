import numpy as np

from kiarina.agi.audio_types import AudioSamples, MonoSamples
from kiarina.agi.vad_model import VADModel
from kiarina.agi.vad_provider import SpeechProbability

from .._schemas.detect_result import DetectResult
from .._schemas.voice import Voice
from .._settings import VoiceDetectorSettings

_BufferItem = tuple[int, float, MonoSamples]


class VoiceDetector:
    def __init__(
        self,
        vad_model: VADModel,
        settings: VoiceDetectorSettings,
    ) -> None:
        self.vad_model: VADModel = vad_model
        self.settings: VoiceDetectorSettings = settings
        self.in_voice: bool = False
        self._sample_rate: int | None = None
        self._cursor_samples: int = 0
        self._voice_start_samples: int | None = None
        self._last_voice_end_samples: int | None = None
        self._silence_samples: int = 0
        self._pre_buffer: list[_BufferItem] = []
        self._voice_buffer: list[_BufferItem] = []

    @property
    def sample_rate(self) -> int:
        if self._sample_rate is None:  # pragma: no cover
            raise ValueError("VoiceDetector has not received samples yet.")

        return self._sample_rate

    async def detect(
        self, samples: AudioSamples, sample_rate: int, timestamp: float
    ) -> DetectResult:
        self._sample_rate = sample_rate
        samples = _to_mono(samples)
        speech_prob = await self.vad_model.predict(samples, sample_rate)
        is_voice = speech_prob >= self.settings.threshold
        voice = self._accept(samples, timestamp, speech_prob)
        return DetectResult(is_voice=is_voice, probability=speech_prob, voice=voice)

    def flush(self) -> Voice | None:
        if not self.in_voice:
            return None

        return self._emit()

    def _accept(
        self, samples: MonoSamples, timestamp: float, speech_prob: SpeechProbability
    ) -> Voice | None:
        samples = np.asarray(samples)
        chunk_start = self._cursor_samples
        chunk_samples = len(samples)
        chunk_end = chunk_start + chunk_samples
        self._cursor_samples = chunk_end

        if speech_prob >= self.settings.threshold:
            self._accept_voice(chunk_start, chunk_end, timestamp, samples)
            return None

        if not self.in_voice:
            self._add_pre_buffer(chunk_start, timestamp, samples)
            return None

        self._silence_samples += chunk_samples

        pad_samples = self._ms_to_samples(self.settings.voice_pad_ms)

        if (
            self._last_voice_end_samples is not None
            and chunk_start < self._last_voice_end_samples + pad_samples
        ):
            self._voice_buffer.append((chunk_start, timestamp, samples))

        if self._silence_samples >= self._ms_to_samples(self.settings.min_silence_ms):
            return self._emit()

        return None

    def _accept_voice(
        self, chunk_start: int, chunk_end: int, timestamp: float, samples: MonoSamples
    ) -> None:
        if not self.in_voice:
            self.in_voice = True
            self._voice_start_samples = (
                self._pre_buffer[0][0] if self._pre_buffer else chunk_start
            )
            self._voice_buffer = [*self._pre_buffer]
            self._pre_buffer = []

        self._voice_buffer.append((chunk_start, timestamp, samples))
        self._last_voice_end_samples = chunk_end
        self._silence_samples = 0

    def _add_pre_buffer(
        self, chunk_start: int, timestamp: float, samples: MonoSamples
    ) -> None:
        self._pre_buffer.append((chunk_start, timestamp, samples))
        min_start = self._cursor_samples - self._ms_to_samples(
            self.settings.voice_pad_ms
        )
        self._pre_buffer = [item for item in self._pre_buffer if item[0] >= min_start]

    def _emit(self) -> Voice:
        samples = np.concatenate([chunk for _, _, chunk in self._voice_buffer], axis=0)

        start_samples = self._voice_start_samples or 0
        end_samples = self._last_voice_end_samples or self._cursor_samples
        end_samples = min(
            end_samples + self._ms_to_samples(self.settings.voice_pad_ms),
            self._cursor_samples,
        )

        voice = Voice(
            samples=samples,
            sample_rate=self.sample_rate,
            start_timestamp=self._samples_to_timestamp(start_samples),
            end_timestamp=self._samples_to_timestamp(end_samples),
            metadata={
                "threshold": self.settings.threshold,
            },
        )

        self.in_voice = False
        self._voice_start_samples = None
        self._last_voice_end_samples = None
        self._silence_samples = 0
        self._pre_buffer = []
        self._voice_buffer = []

        return voice

    def _ms_to_samples(self, milliseconds: int) -> int:
        return round(milliseconds * self.sample_rate / 1000)

    def _samples_to_timestamp(self, samples: int) -> float:
        for chunk_start, timestamp, chunk in reversed(self._voice_buffer):
            chunk_end = chunk_start + len(chunk)

            if chunk_start <= samples <= chunk_end:
                return timestamp + (samples - chunk_start) / self.sample_rate

        chunk_start, timestamp, _ = self._voice_buffer[-1]
        return timestamp + (samples - chunk_start) / self.sample_rate


def _to_mono(samples: AudioSamples) -> MonoSamples:
    samples = np.asarray(samples)

    if samples.ndim == 1:
        return samples

    if samples.ndim == 2:
        return samples[0] if samples.shape[0] == 1 else samples.mean(axis=0)

    raise ValueError(  # pragma: no cover
        f"samples must be 1D or 2D [Channels, Samples], got shape {samples.shape}."
    )
