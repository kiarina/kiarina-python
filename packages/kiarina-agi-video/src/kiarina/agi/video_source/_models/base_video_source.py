import asyncio
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from .._schemas.video_frame import VideoFrame
from .._types.video_source import VideoSource
from .._types.video_source_name import VideoSourceName


class BaseVideoSource(VideoSource, ABC):
    def __init__(self) -> None:
        self._name: VideoSourceName | None = None

    @property
    def name(self) -> VideoSourceName:
        if self._name is None:  # pragma: no cover
            raise ValueError("VideoSource name is not set.")

        return self._name

    @name.setter
    def name(self, value: VideoSourceName) -> None:
        self._name = value

    @asynccontextmanager
    async def open(self, target: object | None) -> AsyncIterator[None]:
        async with self._open(target):
            yield

    @asynccontextmanager
    async def _open(self, target: object | None) -> AsyncIterator[None]:
        yield

    @abstractmethod
    def read(self, *stop_events: asyncio.Event) -> AsyncIterator[VideoFrame]: ...

    def __str__(self) -> str:
        return self.__class__.__name__
