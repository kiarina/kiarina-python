import asyncio
import os
from typing import TypeAlias, cast

from kiarina.agi.file_utils import normalize_time

try:
    from moviepy import VideoFileClip  # type: ignore
except ImportError as exc:
    raise ImportError(
        "moviepy is required to use VideoFileInfoBuilder. Install it with: "
        "pip install 'kiarina-agi-data-builder[file-info-builder-video]'"
    ) from exc

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
    return await asyncio.to_thread(
        _build_intermediate_video,
        input_file_path,
        output_base_path,
        start_time=start_time,
        end_time=end_time,
    )


def _build_intermediate_video(
    input_file_path: str,
    output_base_path: str,
    *,
    start_time: float = 0.0,
    end_time: float = -1.0,
) -> OutputFilePath | None:
    video = VideoFileClip(input_file_path)

    start_time = normalize_time(start_time, video.duration)
    end_time = normalize_time(end_time, video.duration)

    output_file_path = _get_output_file_path(
        output_base_path, start_time, end_time, video.duration
    )

    if os.path.exists(output_file_path):
        video.close()
        return output_file_path

    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

    if _should_clip(start_time, end_time, video.duration):
        _export_1fps_resized_mp3_mono_16kbps_h264_mp4(
            video.subclipped(start_time, end_time), output_file_path
        )
    else:
        _export_1fps_resized_mp3_mono_16kbps_h264_mp4(video, output_file_path)

    video.close()

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
    video: VideoFileClip,
    output_file_path: OutputFilePath,
) -> None:
    width, height = _calc_resized_dimensions(video.w, video.h)

    cast(
        VideoFileClip, cast(VideoFileClip, video.with_fps(1)).resized((width, height))
    ).write_videofile(
        output_file_path,
        codec=CODEC,
        audio_codec=AUDIO_CODEC,
        ffmpeg_params=FFMPEG_PARAMS,
    )


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
