import asyncio
import logging
import os
import shlex
import shutil
import subprocess
from pathlib import Path
from typing import TypeAlias

from kiarina.agi.file_utils import normalize_time

from .get_ffmpeg_exe import get_ffmpeg_exe
from .read_audio_metadata import read_audio_metadata

logger = logging.getLogger(__name__)

OutputFilePath: TypeAlias = str


async def trim_audio(
    input_file_path: str | Path,
    output_file_path: str | Path,
    *,
    start_time: float = 0.0,
    end_time: float = -1.0,
) -> OutputFilePath:
    metadata = await read_audio_metadata(input_file_path)

    return await asyncio.to_thread(
        _trim_audio,
        input_file_path,
        output_file_path,
        duration=metadata.duration,
        start_time=start_time,
        end_time=end_time,
    )


def _trim_audio(
    input_file_path: str | Path,
    output_file_path: str | Path,
    *,
    duration: float,
    start_time: float = 0.0,
    end_time: float = -1.0,
) -> OutputFilePath:
    input_path = Path(input_file_path)
    output_path = Path(output_file_path)

    start_time = normalize_time(start_time, duration)
    end_time = normalize_time(end_time, duration)

    if start_time >= end_time:
        raise ValueError("start_time must be earlier than end_time")

    os.makedirs(output_path.parent, exist_ok=True)

    if start_time == 0.0 and end_time == duration:
        shutil.copyfile(input_path, output_path)
        return str(output_path)

    _run_ffmpeg_stream_copy(
        input_path,
        output_path,
        start_time=start_time,
        end_time=end_time,
    )

    return str(output_path)


def _run_ffmpeg_stream_copy(
    input_file_path: Path,
    output_file_path: Path,
    *,
    start_time: float,
    end_time: float,
) -> None:
    command = [
        get_ffmpeg_exe(),
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-ss",
        str(start_time),
        "-t",
        str(end_time - start_time),
        "-i",
        str(input_file_path),
        "-map",
        "0:a:0",
        "-vn",
        "-c",
        "copy",
        str(output_file_path),
    ]

    logger.debug("ffmpeg: %s", shlex.join(command))

    result = subprocess.run(
        command,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Failed to trim audio.")
