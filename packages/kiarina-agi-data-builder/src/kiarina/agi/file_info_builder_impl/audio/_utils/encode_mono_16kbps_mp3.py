import asyncio
import logging
import os
import shlex
import subprocess
from pathlib import Path
from typing import TypeAlias

from kiarina.agi.file_utils import normalize_time

from .get_ffmpeg_exe import get_ffmpeg_exe
from .read_audio_metadata import read_audio_metadata

logger = logging.getLogger(__name__)

OutputFilePath: TypeAlias = str

CODEC = "libmp3lame"
FFMPEG_PARAMS = ["-ac", "1", "-b:a", "16k"]


async def encode_mono_16kbps_mp3(
    input_file_path: str | Path,
    output_file_path: str | Path,
    *,
    start_time: float = 0.0,
    end_time: float = -1.0,
) -> OutputFilePath:
    metadata = await read_audio_metadata(input_file_path)
    start_time = normalize_time(start_time, metadata.duration)
    end_time = normalize_time(end_time, metadata.duration)

    if start_time >= end_time:
        raise ValueError("start_time must be earlier than end_time")

    return await asyncio.to_thread(
        _encode_mono_16kbps_mp3,
        input_file_path,
        output_file_path,
        duration=metadata.duration,
        start_time=start_time,
        end_time=end_time,
    )


def _encode_mono_16kbps_mp3(
    input_file_path: str | Path,
    output_file_path: str | Path,
    *,
    duration: float,
    start_time: float,
    end_time: float,
) -> OutputFilePath:
    input_path = Path(input_file_path)
    output_path = Path(output_file_path)
    os.makedirs(output_path.parent, exist_ok=True)

    command = [
        get_ffmpeg_exe(),
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
    ]

    if _should_clip(start_time, end_time, duration):
        command.extend(["-ss", str(start_time), "-t", str(end_time - start_time)])

    command.extend(
        [
            "-i",
            str(input_path),
            "-vn",
            "-codec:a",
            CODEC,
            *FFMPEG_PARAMS,
            str(output_path),
        ]
    )

    logger.debug("ffmpeg: %s", shlex.join(command))

    result = subprocess.run(
        command,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Failed to encode audio.")

    return str(output_path)


def _should_clip(start_time: float, end_time: float, duration: float) -> bool:
    return start_time > 0.0 or end_time < duration
