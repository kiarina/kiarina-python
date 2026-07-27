import asyncio
import logging
import os
import shlex
import subprocess
from pathlib import Path

from .._utils.get_ffmpeg_exe import get_ffmpeg_exe

logger = logging.getLogger(__name__)


async def extract_audio_track(
    input_file_path: str,
    output_file_path: str,
) -> str:
    if os.path.exists(output_file_path):
        return output_file_path

    return await asyncio.to_thread(
        _extract_audio_track,
        input_file_path,
        output_file_path,
    )


def _extract_audio_track(input_file_path: str, output_file_path: str) -> str:
    output_path = Path(output_file_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        get_ffmpeg_exe(),
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        input_file_path,
        "-map",
        "0:a:0",
        "-vn",
        "-codec:a",
        "libmp3lame",
        "-ac",
        "1",
        "-b:a",
        "16k",
        output_file_path,
    ]
    logger.debug("ffmpeg: %s", shlex.join(command))

    result = subprocess.run(
        command,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        output_path.unlink(missing_ok=True)
        raise RuntimeError(result.stderr.strip() or "Failed to extract audio track.")

    return output_file_path
