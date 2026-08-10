from typing import Protocol, runtime_checkable

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext

from .audio_file_path import AudioFilePath
from .output_format import OutputFormat
from .tts_provider_name import TTSProviderName


@runtime_checkable
class TTSProvider(Protocol):
    name: TTSProviderName

    async def text_to_speech(
        self,
        text: str,
        *,
        instructions: str | None = None,
        output_format: OutputFormat,
        ignore_cache: bool = False,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> AudioFilePath: ...
