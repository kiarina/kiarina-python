import json
import logging
from abc import ABC, abstractmethod
from hashlib import sha256
from pathlib import Path
from typing import Any

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.cost_recorder_impl.null import NullCostRecorder
from kiarina.agi.file import FilePath
from kiarina.agi.local_repository import create_local_repository
from kiarina.agi.run_context import RunContext

from .._types.audio_file_path import AudioFilePath
from .._types.output_format import OutputFormat
from .._types.tts_provider import TTSProvider
from .._types.tts_provider_name import TTSProviderName

logger = logging.getLogger(__name__)


class BaseTTSProvider(TTSProvider, ABC):
    def __init__(self) -> None:
        self._name: TTSProviderName | None = None

    @property
    def name(self) -> TTSProviderName:
        if self._name is None:
            raise ValueError("TTSProvider name is not set.")

        return self._name

    @name.setter
    def name(self, value: TTSProviderName) -> None:
        self._name = value

    async def text_to_speech(
        self,
        text: str,
        *,
        instructions: str | None = None,
        output_format: OutputFormat,
        ignore_cache: bool = False,
        cost_recorder: CostRecorder | None = None,
        run_context: RunContext,
    ) -> AudioFilePath:
        if not cost_recorder:
            cost_recorder = NullCostRecorder()

        output_file_path = self._generate_cache_path(
            text,
            instructions,
            output_format,
            run_context,
        )
        local_repository = create_local_repository(run_context)

        if not ignore_cache:
            if await local_repository.exists(output_file_path):
                logger.info(f"TTSProvider '{self.name}' cache hit: {output_file_path}")
                return output_file_path

        logger.info(f"TTSProvider '{self.name}' started. text length: {len(text)}")

        await self._text_to_speech(
            text,
            instructions=instructions,
            output_format=output_format,
            output_file_path=output_file_path,
            cost_recorder=cost_recorder,
            run_context=run_context,
        )

        if not await local_repository.exists(output_file_path):  # pragma: no cover
            raise FileNotFoundError(
                f"Could not read generated TTS file: {output_file_path}"
            )

        file_size = Path(output_file_path).stat().st_size

        if file_size == 0:
            raise RuntimeError(f"Generated TTS file is empty: {output_file_path}")

        logger.info(
            f"TTSProvider '{self.name}' completed. "
            f"file_path: {output_file_path}, "
            f"size: {file_size} "
        )

        return output_file_path

    def _generate_cache_path(
        self,
        text: str,
        instructions: str | None,
        output_format: OutputFormat,
        run_context: RunContext,
    ) -> FilePath:
        local_repository = create_local_repository(run_context)

        cache_key = self._generate_cache_key(
            text,
            instructions,
        )

        extension = self._get_output_extension(output_format)
        file_name = f"output{extension}"
        relative_path = Path("tts") / self.name / cache_key / file_name

        return local_repository.generate_cache_path(relative_path)

    def _generate_cache_key(
        self,
        text: str,
        instructions: str | None,
    ) -> str:
        cache_key_args = self._generate_cache_key_args(text, instructions)

        cache_key_json = json.dumps(
            cache_key_args,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )

        return sha256(cache_key_json.encode()).hexdigest()

    def _generate_cache_key_args(
        self,
        text: str,
        instructions: str | None,
    ) -> dict[str, Any]:
        return {
            "text": text,
            "instructions": instructions or "",
        }

    def _get_output_extension(self, output_format: OutputFormat) -> str:
        return f".{output_format}".lower()

    @abstractmethod
    async def _text_to_speech(
        self,
        text: str,
        *,
        instructions: str | None = None,
        output_format: OutputFormat,
        output_file_path: AudioFilePath,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> None: ...

    def __str__(self) -> str:
        return self.__class__.__name__
