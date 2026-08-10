import asyncio
import logging
import re
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .get_ffmpeg_exe import get_ffmpeg_exe

logger = logging.getLogger(__name__)


@dataclass
class AudioMetadata:
    duration: float
    fps: float
    nchannels: int


async def read_audio_metadata(file_path: str | Path) -> AudioMetadata:
    return await asyncio.to_thread(_read_audio_metadata, file_path)


def _read_audio_metadata(file_path: str | Path) -> AudioMetadata:
    command = [
        get_ffmpeg_exe(),
        "-hide_banner",
        "-i",
        str(file_path),
    ]
    logger.debug("ffmpeg: %s", shlex.join(command))

    result = subprocess.run(
        command,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
    )

    output = result.stderr

    return AudioMetadata(
        duration=_parse_duration(output),
        fps=_parse_sample_rate(output),
        nchannels=_parse_channel_count(output),
    )


def _parse_duration(output: str) -> float:
    match = re.search(
        r"Duration:\s*(?P<hours>\d+):(?P<minutes>\d+):(?P<seconds>\d+(?:\.\d+)?)",
        output,
    )

    if not match:
        raise RuntimeError("Audio duration was not found.")

    return (
        int(match["hours"]) * 3600
        + int(match["minutes"]) * 60
        + float(match["seconds"])
    )


def _parse_sample_rate(output: str) -> float:
    match = re.search(r"Audio:.*?,\s*(?P<sample_rate>\d+)\s*Hz", output)

    if not match:
        raise RuntimeError("Audio sample rate was not found.")

    return float(match["sample_rate"])


def _parse_channel_count(output: str) -> int:
    match = re.search(
        r"Audio:.*?,\s*\d+\s*Hz,\s*(?P<channel_layout>[^,\n]+)",
        output,
    )

    if not match:
        raise RuntimeError("Audio channel count was not found.")

    return _channel_layout_to_count(match["channel_layout"].strip())


def _channel_layout_to_count(channel_layout: str) -> int:
    if channel_layout == "mono":
        return 1
    if channel_layout == "stereo":
        return 2

    if match := re.fullmatch(r"(?P<count>\d+)\s+channels?", channel_layout):
        return int(match["count"])

    if match := re.fullmatch(r"(?P<front>\d+)\.(?P<low_frequency>\d+)", channel_layout):
        return int(match["front"]) + int(match["low_frequency"])

    if match := re.fullmatch(
        r"(?P<front>\d+)\.(?P<side>\d+)\.(?P<low_frequency>\d+)",
        channel_layout,
    ):
        return int(match["front"]) + int(match["side"]) + int(match["low_frequency"])

    raise RuntimeError(f"Unsupported audio channel layout: {channel_layout}")
