import asyncio
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import numpy as np

from kiarina.agi.video_source import (
    BaseVideoSource,
    VideoFrame,
    ensure_image_pixels,
)

from .._settings import NumpyVideoSourceSettings


class NumpyVideoSource(BaseVideoSource):
    def __init__(self, settings: NumpyVideoSourceSettings) -> None:
        super().__init__()

        self.settings: NumpyVideoSourceSettings = settings
        self._frames: np.ndarray | None = None
        self._start_timestamp: float | None = None

    @property
    def frames(self) -> np.ndarray:
        if self._frames is None:
            raise AssertionError("frames is not set")

        return self._frames

    @property
    def start_timestamp(self) -> float:
        if self._start_timestamp is None:
            raise AssertionError("start_timestamp is not set")

        return self._start_timestamp

    @asynccontextmanager
    async def _open(self, target: object | None) -> AsyncIterator[None]:
        if target is None:  # pragma: no cover
            raise TypeError("NumpyVideoSource target must be a numpy-compatible array")

        frames = np.asarray(target)

        if frames.ndim == 3:
            frames = frames[np.newaxis, :]
        elif frames.ndim != 4:  # pragma: no cover
            raise ValueError(
                "NumpyVideoSource target must be 3D [Height, Width, Channels] "
                "or 4D [Frames, Height, Width, Channels]"
            )

        if frames.shape[3] != 3:
            raise ValueError(
                "NumpyVideoSource target must have 3 RGB channels, "
                f"got shape {frames.shape}"
            )

        if frames.dtype != np.uint8:
            raise ValueError(
                f"NumpyVideoSource target must have dtype uint8, got {frames.dtype}"
            )

        self._frames = frames
        self._start_timestamp = (
            self.settings.start_timestamp
            if self.settings.start_timestamp is not None
            else time.time()
        )

        try:
            yield
        finally:
            self._frames = None
            self._start_timestamp = None

    async def read(self, *stop_events: asyncio.Event) -> AsyncIterator[VideoFrame]:
        for frame_index, pixels in enumerate(self.frames):
            if any(event.is_set() for event in stop_events):
                break

            yield VideoFrame(
                pixels=ensure_image_pixels(pixels),
                timestamp=self.start_timestamp + frame_index / self.settings.fps,
                frame_index=frame_index,
            )
