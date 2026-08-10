import asyncio
import logging
import shlex
import subprocess
from pathlib import Path

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext
from kiarina.agi.tts_provider import AudioFilePath, BaseTTSProvider, OutputFormat
from kiarina.utils.file.asyncio import read_file

from .._settings import MockTTSProviderSettings
from .._utils.get_ffmpeg_exe import get_ffmpeg_exe

logger = logging.getLogger(__name__)


class MockTTSProvider(BaseTTSProvider):
    def __init__(self, settings: MockTTSProviderSettings) -> None:
        super().__init__()

        self.settings: MockTTSProviderSettings = settings

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
        logger.info(f"Mock TTS: {text[:50]}...")

        if not self.settings.result_audio_file_path:
            raise ValueError(
                "result_audio_file_path must be set in settings for MockTTSProvider"
            )

        file_blob = await read_file(self.settings.result_audio_file_path)

        if not file_blob:
            raise FileNotFoundError(
                f"Could not read file at {self.settings.result_audio_file_path}"
            )

        output_path = Path(output_file_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        command = [
            get_ffmpeg_exe(),
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            "pipe:0",
            "-vn",
            "-f",
            _get_ffmpeg_output_format(output_format),
            str(output_path),
        ]
        logger.debug("ffmpeg: %s", shlex.join(command))

        result = await asyncio.to_thread(
            subprocess.run,
            command,
            input=file_blob.mime_blob.raw_data,
            capture_output=True,
        )

        if result.returncode != 0:
            output_path.unlink(missing_ok=True)
            raise RuntimeError(
                result.stderr.decode(errors="replace").strip()
                or "Failed to convert mock TTS audio."
            )


def _get_ffmpeg_output_format(output_format: OutputFormat) -> str:
    return "adts" if output_format == "aac" else output_format
