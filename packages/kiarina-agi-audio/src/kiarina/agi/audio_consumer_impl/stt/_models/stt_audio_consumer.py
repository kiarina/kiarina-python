from kiarina.agi import asr_model
from kiarina.agi.audio_consumer import BaseAudioConsumer
from kiarina.agi.audio_embedding_model import embed_audio
from kiarina.agi.audio_source import AudioChunk
from kiarina.agi.embedding import Embedding, calc_cosine_similarity
from kiarina.agi.scd_model import SCDModel, scd_model_registry
from kiarina.agi.speaker_change_detector import (
    SpeakerChangeDetector,
    Speech,
    create_speaker_change_detector,
)
from kiarina.agi.vad_model import VADModel, vad_model_registry
from kiarina.agi.voice_detector import (
    Voice,
    VoiceDetector,
    create_voice_detector,
)

from .._schemas.stt_audio_event import STTAudioEvent
from .._settings import STTAudioConsumerSettings


class STTAudioConsumer(BaseAudioConsumer[STTAudioEvent]):
    def __init__(self, settings: STTAudioConsumerSettings) -> None:
        super().__init__()

        self.settings: STTAudioConsumerSettings = settings
        self.speakers: list[list[Embedding]] = []
        self._vad_model: VADModel | None = None
        self._voice_detector: VoiceDetector | None = None
        self._scd_model: SCDModel | None = None
        self._speaker_change_detector: SpeakerChangeDetector | None = None

    @property
    def vad_model(self) -> VADModel:
        if not self._vad_model:
            self._vad_model = vad_model_registry.resolve(self.settings.vad_model)

        return self._vad_model

    @property
    def voice_detector(self) -> VoiceDetector:
        if not self._voice_detector:
            self._voice_detector = create_voice_detector(
                self.vad_model,
                **_drop_none(
                    {
                        "threshold": self.settings.vad_threshold,
                        "min_silence_ms": self.settings.min_silence_ms,
                        "voice_pad_ms": self.settings.voice_pad_ms,
                    }
                ),
            )

        return self._voice_detector

    @property
    def scd_model(self) -> SCDModel:
        if not self._scd_model:
            self._scd_model = scd_model_registry.resolve(self.settings.scd_model)

        return self._scd_model

    @property
    def speaker_change_detector(self) -> SpeakerChangeDetector:
        if not self._speaker_change_detector:
            self._speaker_change_detector = create_speaker_change_detector(
                self.scd_model,
                **_drop_none(
                    {
                        "threshold": self.settings.scd_threshold,
                        "overlap_margin": self.settings.overlap_margin,
                        "min_change_ms": self.settings.min_change_ms,
                        "min_speech_ms": self.settings.min_speech_ms,
                    }
                ),
            )

        return self._speaker_change_detector

    async def accept(self, chunk: AudioChunk) -> list[STTAudioEvent]:
        result = await self.voice_detector.detect(
            chunk.samples,
            chunk.sample_rate,
            chunk.timestamp,
        )

        if result.voice is not None:
            return await self._accept_voice(result.voice)

        return []

    async def flush(self) -> list[STTAudioEvent]:
        if voice := self.voice_detector.flush():
            return await self._accept_voice(voice)

        return []

    async def _accept_voice(self, voice: Voice) -> list[STTAudioEvent]:
        events: list[STTAudioEvent] = []

        speeches = await self.speaker_change_detector.detect(
            voice.samples,
            voice.sample_rate,
            voice.start_timestamp,
        )

        for speech in speeches:
            event = await self._accept_speech(speech)
            events.append(event)

        return events

    async def _accept_speech(self, speech: Speech) -> STTAudioEvent:
        text = await asr_model.speech_to_text(
            speech.samples,
            speech.sample_rate,
            asr_options={"asr_model": self.settings.asr_model},
            run_context=self.run_context,
        )

        embedding: Embedding | None = None

        if self.settings.diarization_enabled:
            embedding = await embed_audio(
                speech.samples,
                speech.sample_rate,
                audio_embedding_options={
                    "audio_embedding_model": self.settings.audio_embedding_model
                },
                run_context=self.run_context,
            )

        if speech.kind == "speaker":
            if embedding:
                speech.speaker_index = self._resolve_speaker_index(embedding)
            else:
                speech.speaker_index = 0

        return STTAudioEvent(
            consumer_name=self.name,
            speech=speech,
            text=text,
            embedding=embedding,
        )

    def _resolve_speaker_index(self, embedding: Embedding) -> int:
        best_index = -1
        best_score = -1.0

        for index, vectors in enumerate(self.speakers):
            score = max(calc_cosine_similarity(embedding, v) for v in vectors)

            if score > best_score:
                best_score = score
                best_index = index

        if best_index >= 0 and best_score >= self.settings.speaker_similarity_threshold:
            self.speakers[best_index].append(embedding)
            return best_index

        self.speakers.append([embedding])
        return len(self.speakers) - 1


def _drop_none(values: dict[str, object | None]) -> dict[str, object]:
    return {key: value for key, value in values.items() if value is not None}
