from itertools import pairwise
from typing import Any

import numpy as np
import pytest


async def test_camera_video_source_throttles_to_requested_fps(
    monkeypatch: Any,
) -> None:
    from kiarina.agi.video_source_impl.camera import (
        CameraVideoSource,
        CameraVideoSourceSettings,
    )
    from kiarina.agi.video_source_impl.camera._models import camera_video_source

    class FakeVideoCapture:
        def __init__(self, device: object) -> None:
            self.device = device
            self.index = 0
            self.released = False

        def isOpened(self) -> bool:
            return True

        def set(self, prop: int, value: float) -> bool:
            return True

        def read(self) -> tuple[bool, np.ndarray | None]:
            if self.index >= 31:
                return False, None

            self.index += 1
            return True, np.full((2, 3, 3), self.index, dtype=np.uint8)

        def release(self) -> None:
            self.released = True

    class FakeCV2:
        CAP_PROP_FRAME_WIDTH = 3
        CAP_PROP_FRAME_HEIGHT = 4
        CAP_PROP_FPS = 5
        COLOR_BGR2RGB = 6
        VideoCapture = FakeVideoCapture

        @staticmethod
        def cvtColor(pixels: np.ndarray, code: int) -> np.ndarray:
            return pixels

    class FakeTime:
        def __init__(self) -> None:
            self._monotonic = 0.0

        def time(self) -> float:
            return 100.0 + self._monotonic

        def monotonic(self) -> float:
            value = self._monotonic
            self._monotonic += 1.0 / 60.0
            return value

    monkeypatch.setattr(camera_video_source, "cv2", FakeCV2)
    monkeypatch.setattr(camera_video_source, "time", FakeTime())

    video_source = CameraVideoSource(CameraVideoSourceSettings(fps=5))

    async with video_source.open(None):
        frames = [frame async for frame in video_source.read()]

    assert [frame.frame_index for frame in frames] == [0, 1, 2, 3, 4]
    deltas = [
        frame.timestamp - previous_frame.timestamp
        for previous_frame, frame in pairwise(frames)
    ]
    assert all(delta >= 0.2 for delta in deltas)


@pytest.mark.skip(reason="Requires camera access and opencv-python")
async def test_camera_video_source() -> None:
    from kiarina.agi.video_source_impl.camera import (
        CameraVideoSource,
        CameraVideoSourceSettings,
    )

    video_source = CameraVideoSource(CameraVideoSourceSettings())

    async with video_source.open(None):
        async for frame in video_source.read():
            print(
                f"frame: {frame.pixels.shape} {frame.pixels.dtype} "
                f"{frame.timestamp} {frame.frame_index}"
            )
            break

    assert True
