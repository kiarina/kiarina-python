from typing import cast


def get_ffmpeg_exe() -> str:
    try:
        import imageio_ffmpeg  # type: ignore

        return cast(str, imageio_ffmpeg.get_ffmpeg_exe())
    except ImportError as exc:
        raise ImportError(
            "imageio-ffmpeg is required to use OpenAITTSProvider. "
            "Install it with: pip install "
            "'kiarina-agi-audio[tts-provider-openai]'"
        ) from exc
