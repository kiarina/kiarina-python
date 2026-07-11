import asyncio
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, closing
from pathlib import Path

from kiarina.agi.video_source import (
    BaseVideoSource,
    VideoFrame,
    ensure_image_pixels,
)

from .._operations.read_video_frames import read_video_frames
from .._operations.read_video_metadata import read_video_metadata
from .._settings import FileVideoSourceSettings


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
        metadata = read_video_metadata(str(self.file_path))
        fps = self.settings.fps or metadata.fps

        with closing(
            read_video_frames(
                str(self.file_path),
                width=metadata.width,
                height=metadata.height,
                fps=fps,
            )
        ) as frames:
            for frame_index, pixels in enumerate(frames):
                if any(event.is_set() for event in stop_events):
                    break

                yield VideoFrame(
                    pixels=ensure_image_pixels(pixels),
                    timestamp=self.start_timestamp + frame_index / fps,
                    frame_index=frame_index,
                )
