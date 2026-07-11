import asyncio
import logging
import os
import shlex
import subprocess
from pathlib import Path
from typing import TypeAlias

from kiarina.agi.file_utils import normalize_time

from .._utils.get_ffmpeg_exe import get_ffmpeg_exe
from .read_video_metadata import read_video_metadata

logger = logging.getLogger(__name__)

OutputFilePath: TypeAlias = str

CODEC = "libx264"
"""H.264 codec"""

AUDIO_CODEC = "libmp3lame"
"""mp3 audio codec"""

FFMPEG_PARAMS = ["-crf", "23", "-ac", "1", "-b:a", "16k"]
"""FFmpeg parameters for mono + 16kbps audio encoding"""

MAX_DIMENSION = 1280
"""Maximum dimension for resizing (longer side)"""


async def build_intermediate_video(
    input_file_path: str,
    output_base_path: str,
    *,
    start_time: float = 0.0,
    end_time: float = -1.0,
) -> OutputFilePath | None:
    metadata = await read_video_metadata(input_file_path)
    start_time = normalize_time(start_time, metadata.duration)
    end_time = normalize_time(end_time, metadata.duration)

    if start_time >= end_time:
        raise ValueError("start_time must be earlier than end_time")

    return await asyncio.to_thread(
        _build_intermediate_video,
        input_file_path,
        output_base_path,
        duration=metadata.duration,
        width=metadata.width,
        height=metadata.height,
        start_time=start_time,
        end_time=end_time,
    )


def _build_intermediate_video(
    input_file_path: str,
    output_base_path: str,
    *,
    duration: float,
    width: int,
    height: int,
    start_time: float = 0.0,
    end_time: float = -1.0,
) -> OutputFilePath | None:
    output_file_path = _get_output_file_path(
        output_base_path, start_time, end_time, duration
    )

    if os.path.exists(output_file_path):
        return output_file_path

    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    _export_1fps_resized_mp3_mono_16kbps_h264_mp4(
        input_file_path,
        output_file_path,
        duration=duration,
        width=width,
        height=height,
        start_time=start_time,
        end_time=end_time,
    )

    if not _is_optimized(input_file_path, output_file_path):
        os.remove(output_file_path)
        return None

    return output_file_path


def _get_output_file_path(
    output_base_path: str,
    start_time: float,
    end_time: float,
    duration: float,
) -> OutputFilePath:
    if start_time != 0.0 or end_time != duration:
        return f"{output_base_path}_{start_time:.1f}_{end_time:.1f}.mp4"
    else:
        return f"{output_base_path}.mp4"


def _should_clip(start_time: float, end_time: float, duration: float) -> bool:
    return start_time > 0.0 or end_time < duration


def _export_1fps_resized_mp3_mono_16kbps_h264_mp4(
    input_file_path: str,
    output_file_path: OutputFilePath,
    *,
    duration: float,
    width: int,
    height: int,
    start_time: float,
    end_time: float,
) -> None:
    resized_width, resized_height = _calc_resized_dimensions(width, height)
    command = [
        get_ffmpeg_exe(),
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        input_file_path,
    ]

    if _should_clip(start_time, end_time, duration):
        command.extend(["-ss", str(start_time), "-t", str(end_time - start_time)])

    command.extend(
        [
            "-map",
            "0:v:0",
            "-map",
            "0:a:0?",
            "-vf",
            f"fps=1,scale={resized_width}:{resized_height}",
            "-codec:v",
            CODEC,
            "-pix_fmt",
            "yuv420p",
            "-codec:a",
            AUDIO_CODEC,
            *FFMPEG_PARAMS,
            output_file_path,
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
        Path(output_file_path).unlink(missing_ok=True)
        raise RuntimeError(result.stderr.strip() or "Failed to encode video.")


def _calc_resized_dimensions(width: int, height: int) -> tuple[int, int]:
    max_dimension = MAX_DIMENSION

    if max(width, height) > max_dimension:
        if width > height:
            new_width = max_dimension
            new_height = int(height * max_dimension / width)
        else:
            new_height = max_dimension
            new_width = int(width * max_dimension / height)
    else:
        new_width, new_height = width, height

    return new_width, new_height


def _is_optimized(input_file_path: str, output_file_path: str) -> bool:
    return os.path.getsize(output_file_path) < os.path.getsize(input_file_path)
