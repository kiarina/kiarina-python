import asyncio
import logging
import re
import shlex
import subprocess

from .._schemas.video_metadata import VideoMetadata
from .._utils.get_ffmpeg_exe import get_ffmpeg_exe

logger = logging.getLogger(__name__)


async def read_video_metadata(file_path: str) -> VideoMetadata:
    return await asyncio.to_thread(_read_video_metadata, file_path)


def _read_video_metadata(file_path: str) -> VideoMetadata:
    command = [
        get_ffmpeg_exe(),
        "-hide_banner",
        "-i",
        file_path,
    ]
    logger.debug("ffmpeg: %s", shlex.join(command))

    result = subprocess.run(
        command,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
    )
    output = result.stderr

    duration = _parse_duration(output)
    video_stream = _find_stream_line(output, "Video")
    width, height = _parse_dimensions(video_stream)
    fps = _parse_fps(video_stream)

    return VideoMetadata(
        duration=duration,
        width=width,
        height=height,
        fps=fps,
        total_frames=int(duration * fps),
        has_audio_track=_has_audio_stream(output),
    )


def _parse_duration(output: str) -> float:
    match = re.search(
        r"Duration:\s*(?P<hours>\d+):(?P<minutes>\d+):(?P<seconds>\d+(?:\.\d+)?)",
        output,
    )

    if not match:
        raise RuntimeError("Video duration was not found.")

    return (
        int(match["hours"]) * 3600
        + int(match["minutes"]) * 60
        + float(match["seconds"])
    )


def _find_stream_line(output: str, stream_type: str) -> str:
    for line in output.splitlines():
        if re.match(rf"\s*Stream #\S+.*?: {stream_type}:", line):
            return line

    raise RuntimeError(f"{stream_type} stream was not found.")


def _parse_dimensions(video_stream: str) -> tuple[int, int]:
    match = re.search(
        r"(?P<width>\d{2,5})x(?P<height>\d{2,5})(?:\s+\[[^]]+\])?",
        video_stream,
    )

    if not match:
        raise RuntimeError("Video dimensions were not found.")

    return int(match["width"]), int(match["height"])


def _parse_fps(video_stream: str) -> float:
    match = re.search(r"(?P<fps>\d+(?:\.\d+)?)\s+fps", video_stream)

    if not match:
        raise RuntimeError("Video frame rate was not found.")

    return float(match["fps"])


def _has_audio_stream(output: str) -> bool:
    return any(
        re.match(r"\s*Stream #\S+.*?: Audio:", line) for line in output.splitlines()
    )
