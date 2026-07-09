import asyncio

try:
    from moviepy import VideoFileClip  # type: ignore
except ImportError as exc:
    raise ImportError(
        "moviepy is required to use VideoFileInfoBuilder. Install it with: "
        "pip install 'kiarina-agi-data-builder[file-info-builder-video]'"
    ) from exc

from .._schemas.video_metadata import VideoMetadata


async def read_video_metadata(file_path: str) -> VideoMetadata:
    return await asyncio.to_thread(_read_video_metadata, file_path)


def _read_video_metadata(file_path: str) -> VideoMetadata:
    clip = VideoFileClip(file_path)

    duration = clip.duration
    width, height = clip.size
    fps = clip.fps
    total_frames = int(duration * fps) if fps else 0
    has_audio_track = clip.audio is not None

    clip.close()

    return VideoMetadata(
        duration=duration,
        width=width,
        height=height,
        fps=fps,
        total_frames=total_frames,
        has_audio_track=has_audio_track,
    )
