import asyncio
import logging
import math
from pathlib import Path
from typing import Any

from kiarina.agi.cost_record import CostRecord
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext
from kiarina.agi.tts_provider import AudioFilePath, BaseTTSProvider, OutputFormat

from .._settings import GoogleTTSProviderSettings

try:
    from google import genai
    from google.genai import types
    from pydub import AudioSegment  # type: ignore

    import kiarina.lib.google
except ImportError as exc:
    raise ImportError(
        "google-genai, kiarina-lib-google-auth, and pydub are required to use "
        "GoogleTTSProvider. "
        "Install them with: pip install 'kiarina-agi-audio[tts-provider-google]'"
    ) from exc

logger = logging.getLogger(__name__)


class GoogleTTSProvider(BaseTTSProvider):
    def __init__(self, settings: GoogleTTSProviderSettings) -> None:
        super().__init__()

        self.settings: GoogleTTSProviderSettings = settings
        self._client: genai.Client | None = None

    @property
    def google_auth_settings(self) -> kiarina.lib.google.GoogleSettings:
        return kiarina.lib.google.settings_manager.get_settings(
            self.settings.google_auth_settings_key
        )

    @property
    def credentials(self) -> kiarina.lib.google.Credentials:
        return kiarina.lib.google.get_credentials(
            settings=self.google_auth_settings,
            scopes=[
                "https://www.googleapis.com/auth/cloud-platform",
            ],
        )

    @property
    def client(self) -> genai.Client:
        if self._client is None:
            self._client = genai.Client(
                credentials=self.credentials,
                http_options=types.HttpOptions(
                    timeout=self.settings.timeout_milliseconds,
                ),
            )

        return self._client

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.settings.model_name})"

    def _generate_cache_key_args(
        self,
        text: str,
        instructions: str | None,
    ) -> dict[str, Any]:
        return {
            "text": text,
            "instructions": instructions or "",
            "model_name": self.settings.model_name,
            "voice_name": self.settings.voice_name,
            "speakers": self.settings.speakers,
        }

    def _get_output_extension(self, output_format: OutputFormat) -> str:
        output_extensions = {
            "opus": ".ogg",
        }

        return output_extensions.get(output_format, f".{output_format}")

    async def _text_to_speech(
        self,
        text: str,
        *,
        instructions: str | None = None,
        output_format: OutputFormat,
        output_file_path: AudioFilePath,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> None:
        input_text = text

        if instructions:
            input_text = f"{instructions}\n\n{text}"

        config: dict[str, Any] = {
            "response_modalities": ["AUDIO"],
        }

        if not self.settings.speakers:
            config["speech_config"] = types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=self.settings.voice_name
                    )
                )
            )
        else:
            config["speech_config"] = types.SpeechConfig(
                multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                    speaker_voice_configs=[
                        types.SpeakerVoiceConfig(
                            speaker=speaker_name,
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name=voice_name
                                )
                            ),
                        )
                        for speaker_name, voice_name in self.settings.speakers.items()
                    ]
                )
            )

        response = self.client.models.generate_content(
            model=self.settings.model_name,
            contents=input_text,
            config=types.GenerateContentConfig(**config),
        )

        await asyncio.to_thread(_save_audio, response, output_format, output_file_path)

        cost_recorder.add(self._build_cost_record(response))

    def _build_cost_record(self, response: types.GenerateContentResponse) -> CostRecord:
        input_tokens = 0
        output_tokens = 0

        if response.usage_metadata:
            input_tokens = response.usage_metadata.prompt_token_count or 0
            output_tokens = response.usage_metadata.candidates_token_count or 0

        input_cost = self.settings.input_cost_microdollars_per_1k_tokens
        output_cost = self.settings.output_cost_microdollars_per_1k_tokens

        cost = math.ceil(
            input_cost * input_tokens / 1_000 + output_cost * output_tokens / 1_000
        )

        return CostRecord(
            microdollars=cost,
            kind="tts",
            source="google",
            metadata={
                "model_name": self.settings.model_name,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
            },
        )


def _save_audio(
    response: types.GenerateContentResponse,
    output_format: OutputFormat,
    output_file_path: AudioFilePath,
) -> None:
    pcm_data: bytes | None = None

    if (
        response.candidates
        and response.candidates[0].content
        and response.candidates[0].content.parts
    ):
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                pcm_data = part.inline_data.data
                break

    if not pcm_data:
        raise RuntimeError("Failed to generate audio data")

    audio_segment = AudioSegment(
        data=pcm_data,
        sample_width=2,  # 16-bit = 2 bytes
        frame_rate=24000,  # 24kHz
        channels=1,  # mono
    )

    Path(output_file_path).parent.mkdir(parents=True, exist_ok=True)

    match output_format:
        case "aac":
            audio_segment.export(
                output_file_path, format="adts", codec="aac", bitrate="128k"
            )
        case _:
            audio_segment.export(output_file_path, format=output_format)
