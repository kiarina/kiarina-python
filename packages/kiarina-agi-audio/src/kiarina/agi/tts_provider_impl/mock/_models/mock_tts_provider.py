import logging
from io import BytesIO
from pathlib import Path

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext
from kiarina.agi.tts_provider import AudioFilePath, BaseTTSProvider, OutputFormat
from kiarina.utils.file.asyncio import read_file

from .._settings import MockTTSProviderSettings

try:
    from pydub import AudioSegment  # type: ignore
except ImportError as exc:
    raise ImportError(
        "pydub is required to use MockTTSProvider. "
        "Install it with: pip install 'kiarina-agi-audio[all]'"
    ) from exc

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
        audio_segment = AudioSegment.from_file(BytesIO(file_blob.mime_blob.raw_data))
        audio_segment.export(output_path, format=output_format)
