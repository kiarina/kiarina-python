import shutil
from typing import cast


def get_ffmpeg_exe() -> str:
    try:
        import imageio_ffmpeg  # type: ignore

        return cast(str, imageio_ffmpeg.get_ffmpeg_exe())
    except ImportError:
        ffmpeg = shutil.which("ffmpeg")

        if ffmpeg:
            return ffmpeg

        raise ImportError(
            "imageio-ffmpeg is required to use FileVideoSource without a system "
            "ffmpeg executable. Install it with: "
            "pip install 'kiarina-agi-video[video-source-file]'"
        ) from None
