import asyncio
import logging
import math
import shlex
import subprocess
from pathlib import Path
from typing import Any

from kiarina.agi.cost_record import CostRecord
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext
from kiarina.agi.tts_provider import AudioFilePath, BaseTTSProvider, OutputFormat

from .._settings import OpenAITTSProviderSettings
from .._utils.get_ffmpeg_exe import get_ffmpeg_exe

try:
    import tiktoken
    from openai import AsyncOpenAI

    import kiarina.lib.openai
except ImportError as exc:
    raise ImportError(
        "kiarina-lib-openai, openai, and tiktoken are required to use "
        "OpenAITTSProvider. "
        "Install them with: pip install 'kiarina-agi-audio[tts-provider-openai]'"
    ) from exc

logger = logging.getLogger(__name__)


class OpenAITTSProvider(BaseTTSProvider):
    def __init__(self, settings: OpenAITTSProviderSettings) -> None:
        super().__init__()

        self.settings: OpenAITTSProviderSettings = settings
        self._client: AsyncOpenAI | None = None

    @property
    def openai_settings(self) -> kiarina.lib.openai.OpenAISettings:
        return kiarina.lib.openai.settings_manager.get_settings(
            self.settings.openai_settings_key
        )

    @property
    def client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(
                timeout=self.settings.timeout,
                **self.openai_settings.to_client_kwargs(),
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
            "voice": self.settings.voice,
        }

    def _get_output_extension(self, output_format: OutputFormat) -> str:
        support_formats = {"aac", "flac", "mp3", "opus", "wav"}

        if output_format not in support_formats:
            raise ValueError(f"Unsupported OpenAI TTS output_format: {output_format}")

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
        request_params: dict[str, Any] = {
            "model": self.settings.model_name,
            "input": text,
            "voice": self.settings.voice,
            "response_format": output_format,
        }

        if instructions:
            request_params["instructions"] = instructions

        response = await self.client.audio.speech.create(**request_params)

        audio_data = response.read()

        output_path = Path(output_file_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(audio_data)

        duration_seconds = await asyncio.to_thread(
            _get_audio_duration_seconds, audio_data, output_format
        )

        encoding = tiktoken.encoding_for_model(self.settings.tiktoken_model_name)
        input_tokens = len(encoding.encode(text))

        cost_recorder.add(self._build_cost_record(input_tokens, duration_seconds))

    def _build_cost_record(
        self, input_tokens: int, duration_seconds: float
    ) -> CostRecord:
        input_cost = self.settings.input_cost_microdollars_per_1k_tokens
        output_cost = self.settings.output_cost_microdollars_per_1_minute

        cost = math.ceil(
            input_cost * input_tokens / 1_000 + output_cost * duration_seconds / 60
        )

        return CostRecord(
            microdollars=cost,
            kind="tts",
            source="openai",
            metadata={
                "model_name": self.settings.model_name,
                "input_tokens": input_tokens,
                "duration_seconds": duration_seconds,
            },
        )


def _get_audio_duration_seconds(
    audio_data: bytes,
    input_format: OutputFormat,
) -> float:
    sample_rate = 24000
    sample_width = 2
    channels = 1
    command = [
        get_ffmpeg_exe(),
        "-hide_banner",
        "-loglevel",
        "error",
        "-f",
        "ogg" if input_format == "opus" else input_format,
        "-i",
        "pipe:0",
        "-f",
        "s16le",
        "-codec:a",
        "pcm_s16le",
        "-ar",
        str(sample_rate),
        "-ac",
        str(channels),
        "pipe:1",
    ]
    logger.debug("ffmpeg: %s", shlex.join(command))

    result = subprocess.run(command, input=audio_data, capture_output=True)

    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.decode(errors="replace").strip()
            or "Failed to decode OpenAI TTS audio."
        )

    return len(result.stdout) / (sample_rate * sample_width * channels)
