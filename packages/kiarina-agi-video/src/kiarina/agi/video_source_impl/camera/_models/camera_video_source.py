import asyncio
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from kiarina.agi.video_source import (
    BaseVideoSource,
    VideoFrame,
    ensure_image_pixels,
)

from .._settings import CameraVideoSourceSettings

try:
    import cv2
except ImportError as exc:
    raise ImportError(
        "opencv-python is required to use CameraVideoSource. "
        "Install it with: pip install 'kiarina-agi-video[video-source-camera]'"
    ) from exc


class CameraVideoSource(BaseVideoSource):
    def __init__(self, settings: CameraVideoSourceSettings) -> None:
        super().__init__()

        self.settings: CameraVideoSourceSettings = settings
        self._capture: cv2.VideoCapture | None = None
        self._unix_offset: float | None = None
        self._frame_index: int = 0
        self._last_emitted_timestamp: float | None = None

    @property
    def capture(self) -> cv2.VideoCapture:
        if self._capture is None:
            raise AssertionError("capture is not set")

        return self._capture

    @property
    def unix_offset(self) -> float:
        if self._unix_offset is None:
            raise AssertionError("unix_offset is not set")

        return self._unix_offset

    @asynccontextmanager
    async def _open(self, target: object | None) -> AsyncIterator[None]:
        if target is not None and not isinstance(target, int | str):
            raise TypeError("CameraVideoSource target must be a device id/name or None")

        device = target if target is not None else self.settings.device
        self._capture = cv2.VideoCapture(device)

        if not self._capture.isOpened():
            self._capture.release()
            self._capture = None
            raise RuntimeError(f"Failed to open camera video source: {device}")

        if self.settings.width is not None:
            self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.settings.width)

        if self.settings.height is not None:
            self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.settings.height)

        if self.settings.fps is not None:
            self._capture.set(cv2.CAP_PROP_FPS, self.settings.fps)

        self._unix_offset = time.time() - time.monotonic()
        self._frame_index = 0
        self._last_emitted_timestamp = None

        try:
            yield
        finally:
            self._capture.release()
            self._capture = None
            self._unix_offset = None
            self._frame_index = 0
            self._last_emitted_timestamp = None

    async def read(self, *stop_events: asyncio.Event) -> AsyncIterator[VideoFrame]:
        while not any(event.is_set() for event in stop_events):
            before = time.monotonic()
            ok, pixels = self.capture.read()
            after = time.monotonic()

            if not ok:
                break

            timestamp = self.unix_offset + (before + after) / 2

            if self._should_skip(timestamp):
                continue

            pixels = cv2.cvtColor(pixels, cv2.COLOR_BGR2RGB)

            yield VideoFrame(
                pixels=ensure_image_pixels(pixels),
                timestamp=timestamp,
                frame_index=self._frame_index,
            )
            self._frame_index += 1
            self._last_emitted_timestamp = timestamp

    def _should_skip(self, timestamp: float) -> bool:
        if self.settings.fps is None:
            return False

        if self._last_emitted_timestamp is None:
            return False

        min_interval = 1.0 / self.settings.fps
        return timestamp < self._last_emitted_timestamp + min_interval
