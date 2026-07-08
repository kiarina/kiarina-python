import asyncio
import logging
from pathlib import Path
from typing import Any, cast

from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.run_context import RunContext
from kiarina.agi.tts_provider import AudioFilePath, BaseTTSProvider, OutputFormat

from .._settings import CommandTTSProviderSettings

try:
    from pydub import AudioSegment  # type: ignore
except ImportError as exc:
    raise ImportError(
        "pydub is required to use CommandTTSProvider. "
        "Install it with: pip install 'kiarina-agi-audio[all]'"
    ) from exc

logger = logging.getLogger(__name__)


class CommandTTSProvider(BaseTTSProvider):
    def __init__(self, settings: CommandTTSProviderSettings) -> None:
        super().__init__()

        self.settings: CommandTTSProviderSettings = settings

    def _generate_cache_key_args(
        self,
        text: str,
        instructions: str | None,
    ) -> dict[str, Any]:
        return {
            "text": text,
            "instructions": instructions or "",
            "command_args": self.settings.command_args,
        }

    def _get_output_extension(self, output_format: OutputFormat) -> str:
        if output_format in self.settings.output_extensions:
            return self.settings.output_extensions[output_format]

        return f".{output_format}"

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
        output_file_path_obj = Path(output_file_path)

        dir_path = output_file_path_obj.parent

        input_file_path = dir_path / "input.txt"

        dir_path.mkdir(parents=True, exist_ok=True)
        input_file_path.write_text(text, encoding="utf-8")

        target_output_format = output_format
        target_output_file_path_obj = output_file_path_obj

        if output_format not in self.settings.command_args:
            target_output_format = "wav"
            target_output_file_path_obj = output_file_path_obj.with_suffix(".wav")

        command_args_list = self._format_command_args(
            text=text,
            instructions=instructions or "",
            output_format=target_output_format,
            input_file_path=input_file_path,
            output_file_path=target_output_file_path_obj,
            tmp_dir_path=dir_path,
        )

        logger.debug(f"Working directory: {dir_path}")
        for command_args in command_args_list:
            await self._run_command(command_args)

        if (
            not target_output_file_path_obj.exists()
            or target_output_file_path_obj.stat().st_size == 0
        ):
            raise RuntimeError(
                f"Did not create output file: {target_output_file_path_obj}"
            )

        if target_output_format != output_format:
            await asyncio.to_thread(
                _convert_audio,
                input_file_path=target_output_file_path_obj,
                output_file_path=output_file_path_obj,
                output_format=output_format,
            )

    async def _run_command(self, command_args: list[str]) -> None:
        logger.debug("Running command TTS: %s", command_args)

        process = await asyncio.create_subprocess_exec(
            *command_args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            _, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.settings.timeout,
            )

        except TimeoutError as exc:
            process.kill()
            await process.wait()
            raise TimeoutError(
                f"Timed out after {self.settings.timeout} seconds"
            ) from exc

        if process.returncode != 0:
            raise RuntimeError(
                "Failed with exit code "
                f"{process.returncode}: {stderr.decode(errors='replace')}"
            )

    def _get_command_args(
        self,
        output_format: OutputFormat,
    ) -> list[str] | list[list[str]]:
        key = output_format if output_format in self.settings.command_args else "*"

        if key not in self.settings.command_args:  # pragma: no cover
            raise ValueError(
                f"command_args is not configured for output_format: {output_format}"
            )

        return self.settings.command_args[key]

    def _format_command_args(
        self,
        *,
        text: str,
        instructions: str,
        output_format: OutputFormat,
        input_file_path: Path,
        output_file_path: Path,
        tmp_dir_path: Path,
    ) -> list[list[str]]:
        values = {
            "text": text,
            "instructions": instructions,
            "output_format": output_format,
            "input_file": str(input_file_path),
            "output_file": str(output_file_path),
            "tmp_dir": str(tmp_dir_path),
        }

        try:
            return [
                [arg.format_map(values) for arg in command_args]
                for command_args in self._normalize_command_args(
                    self._get_command_args(output_format)
                )
            ]

        except KeyError as exc:
            raise ValueError(f"Unknown command placeholder: {exc.args[0]}") from exc

    def _normalize_command_args(
        self,
        command_args: list[str] | list[list[str]],
    ) -> list[list[str]]:
        if not command_args:
            raise ValueError("command_args must not be empty")

        if all(isinstance(arg, str) for arg in command_args):
            return [cast(list[str], command_args)]

        if all(
            isinstance(arg, list) and all(isinstance(item, str) for item in arg)
            for arg in command_args
        ):
            return cast(list[list[str]], command_args)

        raise ValueError("command_args must be list[str] or list[list[str]]")


def _convert_audio(
    input_file_path: Path,
    output_file_path: Path,
    output_format: OutputFormat,
) -> None:
    audio_segment: AudioSegment = AudioSegment.from_file(input_file_path, format="wav")

    match output_format:
        case "aac":
            audio_segment.export(
                output_file_path, format="adts", codec="aac", bitrate="128k"
            )
        case _:
            audio_segment.export(output_file_path, format=output_format)
