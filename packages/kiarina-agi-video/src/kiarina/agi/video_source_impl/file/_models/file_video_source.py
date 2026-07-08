import asyncio
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from kiarina.agi.video_source import (
    BaseVideoSource,
    VideoFrame,
    ensure_image_pixels,
)

from .._settings import FileVideoSourceSettings

try:
    from moviepy import VideoFileClip  # type: ignore
except ImportError as exc:
    raise ImportError(
        "moviepy is required to use FileVideoSource. "
        "Install it with: pip install 'kiarina-agi-video[video-source-file]'"
    ) from exc


class FileVideoSource(BaseVideoSource):
    def __init__(self, settings: FileVideoSourceSettings) -> None:
        super().__init__()

        self.settings: FileVideoSourceSettings = settings
        self._file_path: Path | None = None
        self._start_timestamp: float | None = None

    @property
    def file_path(self) -> Path:
        if self._file_path is None:
            raise AssertionError("file_path is not set")

        return self._file_path

    @property
    def start_timestamp(self) -> float:
        if self._start_timestamp is None:
            raise AssertionError("start_timestamp is not set")

        return self._start_timestamp

    @asynccontextmanager
    async def _open(self, target: object | None) -> AsyncIterator[None]:
        if not isinstance(target, str | Path):
            raise TypeError("FileVideoSource target must be a str or Path")

        self._file_path = Path(target).expanduser()
        self._start_timestamp = (
            self.settings.start_timestamp
            if self.settings.start_timestamp is not None
            else time.time()
        )

        try:
            yield
        finally:
            self._file_path = None
            self._start_timestamp = None

    async def read(self, *stop_events: asyncio.Event) -> AsyncIterator[VideoFrame]:
        with VideoFileClip(str(self.file_path)) as clip:
            fps = self.settings.fps or float(clip.fps)

            for frame_index, pixels in enumerate(
                clip.iter_frames(fps=fps, dtype="uint8")
            ):
                if any(event.is_set() for event in stop_events):
                    break

                yield VideoFrame(
                    pixels=ensure_image_pixels(pixels),
                    timestamp=self.start_timestamp + frame_index / fps,
                    frame_index=frame_index,
                )
