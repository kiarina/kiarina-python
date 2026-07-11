import logging
import re
import shlex
import subprocess

from .._schemas.video_metadata import VideoMetadata
from .._utils.get_ffmpeg_exe import get_ffmpeg_exe

logger = logging.getLogger(__name__)


def read_video_metadata(file_path: str) -> VideoMetadata:
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
    video_stream = _find_video_stream(result.stderr)

    return VideoMetadata(
        width=_parse_dimension(video_stream, "width"),
        height=_parse_dimension(video_stream, "height"),
        fps=_parse_fps(video_stream),
    )


def _find_video_stream(output: str) -> str:
    for line in output.splitlines():
        if re.match(r"\s*Stream #\S+.*?: Video:", line):
            return line

    raise RuntimeError("Video stream was not found.")


def _parse_dimension(video_stream: str, name: str) -> int:
    match = re.search(
        r"(?P<width>\d{2,5})x(?P<height>\d{2,5})(?:\s+\[[^]]+\])?",
        video_stream,
    )

    if not match:
        raise RuntimeError("Video dimensions were not found.")

    return int(match[name])


def _parse_fps(video_stream: str) -> float:
    match = re.search(r"(?P<fps>\d+(?:\.\d+)?)\s+fps", video_stream)

    if not match:
        raise RuntimeError("Video frame rate was not found.")

    return float(match["fps"])
