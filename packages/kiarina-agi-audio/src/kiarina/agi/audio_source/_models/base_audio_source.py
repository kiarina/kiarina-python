import asyncio
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from .._schemas.audio_chunk import AudioChunk
from .._types.audio_source import AudioSource
from .._types.audio_source_name import AudioSourceName


class BaseAudioSource(AudioSource, ABC):
    def __init__(self) -> None:
        self._name: AudioSourceName | None = None

    @property
    def name(self) -> AudioSourceName:
        if self._name is None:  # pragma: no cover
            raise ValueError("AudioSource name is not set.")

        return self._name

    @name.setter
    def name(self, value: AudioSourceName) -> None:
        self._name = value

    @asynccontextmanager
    async def open(self, target: object | None) -> AsyncIterator[None]:
        async with self._open(target):
            yield

    @asynccontextmanager
    async def _open(self, target: object | None) -> AsyncIterator[None]:
        yield

    @abstractmethod
    def read(self, *stop_events: asyncio.Event) -> AsyncIterator[AudioChunk]: ...

    def __str__(self) -> str:
        return self.__class__.__name__
