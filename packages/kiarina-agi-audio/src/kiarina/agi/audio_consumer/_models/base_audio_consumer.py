from typing import TypeVar

from kiarina.agi.run_context import RunContext

from .._schemas.audio_event import AudioEvent
from .._types.audio_consumer import AudioConsumer
from .._types.audio_consumer_name import AudioConsumerName

T = TypeVar("T", bound=AudioEvent)


class BaseAudioConsumer(AudioConsumer[T]):
    def __init__(self) -> None:
        self._name: AudioConsumerName | None = None
        self._run_context: RunContext | None = None

    @property
    def name(self) -> AudioConsumerName:
        if self._name is None:  # pragma: no cover
            raise ValueError("AudioConsumer name is not set.")

        return self._name

    @name.setter
    def name(self, value: AudioConsumerName) -> None:
        self._name = value

    @property
    def run_context(self) -> RunContext:
        if self._run_context is None:
            raise ValueError("run_context is not set.")

        return self._run_context

    @run_context.setter
    def run_context(self, run_context: RunContext) -> None:
        self._run_context = run_context

    def __str__(self) -> str:
        return self.__class__.__name__
