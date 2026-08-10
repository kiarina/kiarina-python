from typing import Protocol, TypeVar, runtime_checkable

from kiarina.agi.audio_source import AudioChunk
from kiarina.agi.run_context import RunContext

from .._schemas.audio_event import AudioEvent
from .audio_consumer_name import AudioConsumerName

T = TypeVar("T", bound=AudioEvent)


@runtime_checkable
class AudioConsumer(Protocol[T]):
    name: AudioConsumerName

    run_context: RunContext

    async def accept(self, chunk: AudioChunk) -> list[T]: ...

    async def flush(self) -> list[T]: ...
