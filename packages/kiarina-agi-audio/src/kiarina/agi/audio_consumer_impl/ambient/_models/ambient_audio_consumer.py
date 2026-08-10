import numpy as np

from kiarina.agi.audio_consumer import BaseAudioConsumer
from kiarina.agi.audio_embedding_model import (
    embed_audio,
)
from kiarina.agi.audio_source import AudioChunk
from kiarina.agi.audio_tagging_model import (
    AudioTaggingOptions,
    tag_audio,
)
from kiarina.agi.audio_types import AudioSamples, MonoSamples
from kiarina.agi.audio_window import AudioWindow, AudioWindowBuffer

from .._schemas.ambient_audio_event import AmbientAudioEvent
from .._settings import AmbientAudioConsumerSettings


class AmbientAudioConsumer(BaseAudioConsumer[AmbientAudioEvent]):
    def __init__(self, settings: AmbientAudioConsumerSettings) -> None:
        super().__init__()
        self.settings: AmbientAudioConsumerSettings = settings
        self.window_buffer = AudioWindowBuffer(
            window_seconds=settings.window_seconds,
            window_samples=settings.window_samples,
        )

    async def accept(self, chunk: AudioChunk) -> list[AmbientAudioEvent]:
        windows = self.window_buffer.accept(
            _to_mono(chunk.samples),
            sample_rate=chunk.sample_rate,
            timestamp=chunk.timestamp,
        )

        return await self._analyze_windows(windows)

    async def flush(self) -> list[AmbientAudioEvent]:
        return await self._analyze_windows(self.window_buffer.flush())

    async def _analyze_windows(
        self,
        windows: list[AudioWindow],
    ) -> list[AmbientAudioEvent]:
        events: list[AmbientAudioEvent] = []

        for window in windows:
            event = await self._analyze_window(window)
            events.append(event)

        return events

    async def _analyze_window(self, window: AudioWindow) -> AmbientAudioEvent:
        audio_tagging_options: AudioTaggingOptions = {
            "top_k": self.settings.top_k,
        }

        if self.settings.audio_tagging_model is not None:
            audio_tagging_options["audio_tagging_model"] = (
                self.settings.audio_tagging_model
            )

        if self.settings.tag_threshold is not None:
            audio_tagging_options["threshold"] = self.settings.tag_threshold

        predictions = await tag_audio(
            window.samples,
            window.sample_rate,
            audio_tagging_options=audio_tagging_options,
            run_context=self.run_context,
        )

        embedding = await embed_audio(
            window.samples,
            window.sample_rate,
            audio_embedding_options={
                "audio_embedding_model": self.settings.audio_embedding_model,
            },
            run_context=self.run_context,
        )

        return AmbientAudioEvent(
            consumer_name=self.name,
            start_timestamp=window.start_timestamp,
            end_timestamp=window.end_timestamp,
            predictions=predictions,
            embedding=embedding,
        )


def _to_mono(samples: AudioSamples) -> MonoSamples:
    samples = np.asarray(samples)

    if samples.ndim == 1:
        return samples

    if samples.ndim == 2:
        return samples[0] if samples.shape[0] == 1 else samples.mean(axis=0)

    raise ValueError(  # pragma: no cover
        f"samples must be 1D or 2D [Channels, Samples], got shape {samples.shape}."
    )
