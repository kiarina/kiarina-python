import asyncio
from collections.abc import AsyncIterator
from contextlib import AbstractAsyncContextManager
from typing import Protocol, runtime_checkable

from .._schemas.video_frame import VideoFrame


@runtime_checkable
class VideoSource(Protocol):
    name: str

    def open(self, target: object | None) -> AbstractAsyncContextManager[None]: ...

    def read(self, *stop_events: asyncio.Event) -> AsyncIterator[VideoFrame]: ...
