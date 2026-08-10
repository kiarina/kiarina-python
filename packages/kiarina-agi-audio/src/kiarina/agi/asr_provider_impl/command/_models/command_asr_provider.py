import asyncio
import logging
from pathlib import Path

from kiarina.agi.asr_provider import (
    ASRSegment,
    BaseASRProvider,
    parse_srt,
    write_wav,
)
from kiarina.agi.audio_types import MonoSamples
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.local_repository import create_local_repository
from kiarina.agi.run_context import RunContext

from .._settings import CommandASRProviderSettings
from .._types.input_mode import InputMode

logger = logging.getLogger(__name__)


class CommandASRProvider(BaseASRProvider):
    def __init__(self, settings: CommandASRProviderSettings) -> None:
        super().__init__()

        self.settings: CommandASRProviderSettings = settings

    @property
    def text_command_args(self) -> list[str]:
        if not self.settings.text_command_args:
            raise ValueError("text_command_args is not set")

        return self.settings.text_command_args

    @property
    def segments_command_args(self) -> list[str]:
        if not self.settings.segments_command_args:
            raise ValueError("segments_command_args is not set")

        return self.settings.segments_command_args

    async def _speech_to_text(
        self,
        samples: MonoSamples,
        sample_rate: int,
        *,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> str:
        return await self._run_command(
            samples,
            sample_rate,
            command_args=self.text_command_args,
            input_mode=self.settings.text_command_input_mode,
            output_file_suffix=self.settings.text_output_file_suffix,
            run_context=run_context,
        )

    async def _speech_to_segments(
        self,
        samples: MonoSamples,
        sample_rate: int,
        *,
        cost_recorder: CostRecorder,
        run_context: RunContext,
    ) -> list[ASRSegment]:
        srt_text = await self._run_command(
            samples,
            sample_rate,
            command_args=self.segments_command_args,
            input_mode=self.settings.segments_command_input_mode,
            output_file_suffix=self.settings.segments_output_file_suffix,
            run_context=run_context,
        )
        return parse_srt(srt_text)

    async def _run_command(
        self,
        samples: MonoSamples,
        sample_rate: int,
        *,
        command_args: list[str],
        input_mode: InputMode,
        output_file_suffix: str,
        run_context: RunContext,
    ) -> str:
        local_repository = create_local_repository(run_context)

        dir_path = Path(
            local_repository.generate_time_based_dir_path(
                sub_dir_path="asr",
                area="cache",
            )
        )

        output_file_path = dir_path / f"output{output_file_suffix}"
        output_file_stem_path = output_file_path.with_suffix("")
        input_file_path: Path | None = None
        stdin_data: bytes | None = None

        dir_path.mkdir(parents=True, exist_ok=True)

        if input_mode == "file":
            input_file_path = dir_path / "input.wav"
            write_wav(input_file_path, samples, sample_rate)
        else:
            stdin_data = self._encode_wav(samples, sample_rate)

        command_args = self._format_command_args(
            command_args=command_args,
            input_file_path=input_file_path,
            output_file_path=output_file_path,
            output_file_stem_path=output_file_stem_path,
            tmp_dir_path=dir_path,
        )

        logger.debug("Running command ASR: %s", command_args)

        process = await asyncio.create_subprocess_exec(
            *command_args,
            stdin=asyncio.subprocess.PIPE if stdin_data is not None else None,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            _, stderr = await asyncio.wait_for(
                process.communicate(input=stdin_data),
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

        if not output_file_path.exists() or output_file_path.stat().st_size == 0:
            raise RuntimeError(f"Did not create output file: {output_file_path}")

        text = output_file_path.read_text(
            encoding=self.settings.encoding,
        ).strip()

        return text

    def _format_command_args(
        self,
        *,
        command_args: list[str],
        input_file_path: Path | None,
        output_file_path: Path,
        output_file_stem_path: Path,
        tmp_dir_path: Path,
    ) -> list[str]:
        values = {
            "input_file": str(input_file_path or ""),
            "output_file": str(output_file_path),
            "output_file_stem": str(output_file_stem_path),
            "tmp_dir": str(tmp_dir_path),
        }

        try:
            return [arg.format_map(values) for arg in command_args]
        except KeyError as exc:
            raise ValueError(f"Unknown command placeholder: {exc.args[0]}") from exc
