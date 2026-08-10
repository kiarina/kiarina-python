import asyncio
from collections.abc import AsyncIterator
from contextlib import AbstractAsyncContextManager
from typing import Protocol, runtime_checkable

from .._schemas.audio_chunk import AudioChunk


@runtime_checkable
class AudioSource(Protocol):
    name: str

    def open(self, target: object | None) -> AbstractAsyncContextManager[None]: ...

    def read(self, *stop_events: asyncio.Event) -> AsyncIterator[AudioChunk]: ...
