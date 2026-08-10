import logging
import shlex
import subprocess
from collections.abc import Generator
from typing import IO

import numpy as np

from kiarina.agi.image_types import ImagePixels

from .._utils.get_ffmpeg_exe import get_ffmpeg_exe

logger = logging.getLogger(__name__)


def read_video_frames(
    file_path: str,
    *,
    width: int,
    height: int,
    fps: float,
) -> Generator[ImagePixels, None, None]:
    command = [
        get_ffmpeg_exe(),
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        file_path,
        "-map",
        "0:v:0",
        "-an",
        "-vf",
        f"fps={fps}",
        "-pix_fmt",
        "rgb24",
        "-f",
        "rawvideo",
        "pipe:1",
    ]
    logger.debug("ffmpeg: %s", shlex.join(command))

    frame_size = width * height * 3
    process = subprocess.Popen(
        command,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=frame_size,
    )

    if process.stdout is None or process.stderr is None:
        process.kill()
        raise RuntimeError("Failed to open ffmpeg pipes.")

    completed = False
    try:
        while frame_data := _read_frame(process.stdout, frame_size):
            pixels = np.frombuffer(frame_data, dtype=np.uint8).reshape(
                (height, width, 3)
            )
            yield pixels.copy()

        stderr = process.stderr.read().decode(errors="replace").strip()
        returncode = process.wait()
        completed = True

        if returncode != 0:
            raise RuntimeError(stderr or "Failed to read video frames.")
    finally:
        process.stdout.close()
        process.stderr.close()

        if not completed and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


def _read_frame(stream: IO[bytes], frame_size: int) -> bytes:
    read = stream.read
    frame_data = bytearray()

    while len(frame_data) < frame_size:
        chunk = read(frame_size - len(frame_data))
        if not chunk:
            break
        frame_data.extend(chunk)

    if frame_data and len(frame_data) != frame_size:
        raise RuntimeError("ffmpeg returned an incomplete video frame.")

    return bytes(frame_data)
