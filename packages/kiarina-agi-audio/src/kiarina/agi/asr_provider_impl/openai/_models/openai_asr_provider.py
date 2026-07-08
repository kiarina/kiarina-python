import io
import logging
import math
from typing import Any

from kiarina.agi.asr_provider import ASRSegment, BaseASRProvider
from kiarina.agi.audio_types import MonoSamples
from kiarina.agi.cost_record import CostRecord
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext
from kiarina.utils.file.asyncio import read_file

from .._settings import OpenAIASRProviderSettings

try:
    from openai import AsyncOpenAI

    import kiarina.lib.openai
except ImportError as exc:
    raise ImportError(
        "kiarina-lib-openai and openai are required to use OpenAIASRProvider. "
        "Install them with: pip install 'kiarina-agi-audio[asr-provider-openai]'"
    ) from exc

logger = logging.getLogger(__name__)


class OpenAIASRProvider(BaseASRProvider):
    def __init__(self, settings: OpenAIASRProviderSettings) -> None:
        super().__init__()

        self.settings: OpenAIASRProviderSettings = settings
        self._client: AsyncOpenAI | None = None

    @property
    def client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(
                timeout=self.settings.timeout,
                **kiarina.lib.openai.settings_manager.get_settings(
                    self.settings.openai_settings_key
                ).to_client_kwargs(),
            )

        return self._client

    async def _speech_to_text(
        self,
        samples: MonoSamples,
        sample_rate: int,
        *,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> str:
        audio_file = self._build_audio_file(samples, sample_rate)
        request_params: dict[str, Any] = {
            "model": self.settings.text_model_name,
            "file": audio_file,
        }

        response = await self.client.audio.transcriptions.create(**request_params)

        cost_recorder.add(
            self._build_cost_record(
                response,
                model_name=self.settings.text_model_name,
                input_cost_microdollars_per_1k_tokens=(
                    self.settings.text_input_cost_microdollars_per_1k_tokens
                ),
                output_cost_microdollars_per_1k_tokens=(
                    self.settings.text_output_cost_microdollars_per_1k_tokens
                ),
            )
        )

        return str(response.text)

    async def _speech_to_segments(
        self,
        samples: MonoSamples,
        sample_rate: int,
        *,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> list[ASRSegment]:
        request_params: dict[str, Any] = {
            "model": self.settings.segments_model_name,
            "response_format": "diarized_json",
            "chunking_strategy": "auto",
        }

        if self.settings.speakers:
            known_speaker_names: list[str] = []
            known_speaker_references: list[str] = []

            for speaker_name, voice_file_path in self.settings.speakers.items():
                known_speaker_names.append(speaker_name)

                file_blob = await read_file(voice_file_path)

                if not file_blob:
                    raise FileNotFoundError(
                        f"Reference voice file not found: {voice_file_path}"
                    )

                known_speaker_references.append(file_blob.raw_base64_url)

            request_params.update(
                {
                    "extra_body": {
                        "known_speaker_names": known_speaker_names,
                        "known_speaker_references": known_speaker_references,
                    },
                }
            )

        request_params["file"] = self._build_audio_file(samples, sample_rate)
        response = await self.client.audio.transcriptions.create(**request_params)

        segments: list[ASRSegment] = []

        if hasattr(response, "segments"):
            for segment in response.segments:
                metadata = {}
                if hasattr(segment, "speaker") and segment.speaker:
                    metadata["speaker_name"] = segment.speaker

                segments.append(
                    ASRSegment(
                        text=segment.text,
                        start_timestamp=segment.start,
                        end_timestamp=segment.end,
                        metadata=metadata,
                    )
                )

        cost_recorder.add(
            self._build_cost_record(
                response,
                model_name=self.settings.segments_model_name,
                input_cost_microdollars_per_1k_tokens=(
                    self.settings.segments_input_cost_microdollars_per_1k_tokens
                ),
                output_cost_microdollars_per_1k_tokens=(
                    self.settings.segments_output_cost_microdollars_per_1k_tokens
                ),
            )
        )

        return segments

    def _build_audio_file(self, samples: MonoSamples, sample_rate: int) -> io.BytesIO:
        audio_file = io.BytesIO(self._encode_wav(samples, sample_rate))
        audio_file.name = "input.wav"
        return audio_file

    def _build_cost_record(
        self,
        response: Any,
        *,
        model_name: str,
        input_cost_microdollars_per_1k_tokens: int,
        output_cost_microdollars_per_1k_tokens: int,
    ) -> CostRecord:
        input_tokens = 0
        output_tokens = 0

        if hasattr(response, "usage") and response.usage:
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens

        cost = math.ceil(
            input_cost_microdollars_per_1k_tokens * input_tokens / 1_000
            + output_cost_microdollars_per_1k_tokens * output_tokens / 1_000
        )

        return CostRecord(
            microdollars=cost,
            kind="asr",
            source="openai",
            metadata={
                "model_name": model_name,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "input_cost_microdollars_per_1k_tokens": (
                    input_cost_microdollars_per_1k_tokens
                ),
                "output_cost_microdollars_per_1k_tokens": (
                    output_cost_microdollars_per_1k_tokens
                ),
            },
        )

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.settings.text_model_name})"
