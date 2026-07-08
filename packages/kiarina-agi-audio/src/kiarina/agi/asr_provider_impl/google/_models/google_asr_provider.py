import json
import logging
import math
from typing import Any

from kiarina.agi.asr_provider import ASRSegment, BaseASRProvider
from kiarina.agi.audio_types import MonoSamples
from kiarina.agi.cost_record import CostRecord
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext

from .._settings import GoogleASRProviderSettings

try:
    from google import genai
    from google.genai import types

    import kiarina.lib.google
except ImportError as exc:
    raise ImportError(
        "google-genai and kiarina-lib-google-auth are required to use "
        "GoogleASRProvider. "
        "Install them with: pip install 'kiarina-agi-audio[asr-provider-google]'"
    ) from exc

logger = logging.getLogger(__name__)


class GoogleASRProvider(BaseASRProvider):
    def __init__(self, settings: GoogleASRProviderSettings) -> None:
        super().__init__()

        self.settings: GoogleASRProviderSettings = settings
        self._client: genai.Client | None = None

    @property
    def client(self) -> genai.Client:
        if self._client is None:
            self._client = genai.Client(
                **kiarina.lib.google.get_cloud_options(
                    self.settings.google_auth_settings_key,
                ),
                http_options=types.HttpOptions(
                    timeout=self.settings.timeout_milliseconds,
                ),
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
        response = await self._generate_content(
            samples,
            sample_rate,
            prompt=(
                "Transcribe only the spoken words in the audio. "
                "Do not add speaker labels, translations, romanization, summaries, "
                "headings, explanations, markdown, or any text that was not spoken. "
                "Preserve the original spoken language."
            ),
            config=None,
        )

        if not response.text:
            raise RuntimeError("Failed to generate transcription")

        cost_recorder.add(self._build_cost_record(response))

        return response.text

    async def _speech_to_segments(
        self,
        samples: MonoSamples,
        sample_rate: int,
        *,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> list[ASRSegment]:
        prompt = "Generate a timestamped transcript of the speech"
        segment_properties: dict[str, types.Schema] = {}

        speaker_description = (
            "Identify speakers using generic names such as Speaker 1, Speaker 2."
        )

        if self.settings.speakers:
            speaker_description = (
                "To identify speakers, use the following speaker information:\n"
            )

            for speaker_name, description in self.settings.speakers.items():
                speaker_description += f"- {speaker_name}: {description}\n"

        segment_properties = {
            "speaker": types.Schema(
                type=types.Type.STRING,
                description=speaker_description,
            ),
            "start_time": types.Schema(
                type=types.Type.NUMBER,
                description="The start time of the segment in seconds (float)",
            ),
            "end_time": types.Schema(
                type=types.Type.NUMBER,
                description="The end time of the segment in seconds (float)",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The transcribed content of the segment",
            ),
        }

        segment_required = ["speaker", "start_time", "end_time", "content"]

        for (
            prop_name,
            prop_config,
        ) in self.settings.extra_segment_properties.items():
            prop_type = prop_config.get("type", "string")
            prop_desc = prop_config.get("description")
            prop_enum = prop_config.get("enum")

            if prop_type == "string":
                schema = types.Schema(type=types.Type.STRING)
            elif prop_type == "number":
                schema = types.Schema(type=types.Type.NUMBER)
            elif prop_type == "boolean":
                schema = types.Schema(type=types.Type.BOOLEAN)
            else:
                schema = types.Schema(type=types.Type.STRING)

            if prop_enum:
                schema.enum = prop_enum

            if prop_desc:
                schema.description = prop_desc

            segment_properties[prop_name] = schema
            segment_required.append(prop_name)

        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "segments": types.Schema(
                        type=types.Type.ARRAY,
                        description="List of transcribed segments with speaker and timestamp.",
                        items=types.Schema(
                            type=types.Type.OBJECT,
                            properties=segment_properties,
                            required=segment_required,
                        ),
                    ),
                },
                required=["segments"],
            ),
        )

        response = await self._generate_content(
            samples,
            sample_rate,
            prompt=prompt,
            config=config,
        )

        if not response.text:
            raise RuntimeError("Failed to generate transcription")

        cost_recorder.add(self._build_cost_record(response))

        try:
            response_data = json.loads(response.text)

        except json.JSONDecodeError:
            return []

        segments: list[ASRSegment] = []

        for segment_data in response_data.get("segments", []):
            metadata: dict[str, Any] = {}

            if speaker_name := segment_data.get("speaker"):
                metadata["speaker_name"] = speaker_name

            for prop_name in self.settings.extra_segment_properties.keys():
                if prop_name in segment_data:
                    metadata[prop_name] = segment_data[prop_name]

            segments.append(
                ASRSegment(
                    text=segment_data["content"],
                    start_timestamp=float(segment_data["start_time"]),
                    end_timestamp=float(segment_data["end_time"]),
                    metadata=metadata,
                )
            )

        return segments

    async def _generate_content(
        self,
        samples: MonoSamples,
        sample_rate: int,
        *,
        prompt: str,
        config: types.GenerateContentConfig | None,
    ) -> types.GenerateContentResponse:
        return self.client.models.generate_content(
            model=self.settings.model_name,
            contents=types.Content(
                parts=[
                    types.Part.from_bytes(
                        data=self._encode_wav(samples, sample_rate),
                        mime_type="audio/wav",
                    ),
                    types.Part(text=prompt),
                ]
            ),
            config=config,
        )

    def _build_cost_record(self, response: types.GenerateContentResponse) -> CostRecord:
        input_tokens = 0
        input_audio_tokens = 0
        output_tokens = 0

        if response.usage_metadata:
            if response.usage_metadata.prompt_tokens_details:
                for detail in response.usage_metadata.prompt_tokens_details:
                    if detail.modality == "AUDIO":
                        input_audio_tokens = detail.token_count or 0
                    else:
                        input_tokens += detail.token_count or 0

            if response.usage_metadata.thoughts_token_count:
                input_tokens += response.usage_metadata.thoughts_token_count

            output_tokens = response.usage_metadata.candidates_token_count or 0

        input_cost = self.settings.input_cost_microdollars_per_1k_tokens
        input_audio_cost = self.settings.input_audio_cost_microdollars_per_1k_tokens
        output_cost = self.settings.output_cost_microdollars_per_1k_tokens

        cost = math.ceil(
            input_cost * input_tokens / 1_000
            + input_audio_cost * input_audio_tokens / 1_000
            + output_cost * output_tokens / 1_000
        )

        return CostRecord(
            microdollars=cost,
            kind="asr",
            source="google",
            metadata={
                "model_name": self.settings.model_name,
                "input_tokens": input_tokens,
                "input_audio_tokens": input_audio_tokens,
                "output_tokens": output_tokens,
            },
        )

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.settings.model_name})"
