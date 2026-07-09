from typing import Protocol, runtime_checkable

from kiarina.agi.audio_consumer import AudioEvent
from kiarina.agi.file_bundle import FileBundle

from .audio_event_bundler_name import AudioEventBundlerName


@runtime_checkable
class AudioEventBundler(Protocol):
    """
    Format a list of :class:`AudioEvent` instances into a :class:`FileBundle`.

    Implementations should filter ``events`` for the event subtype they care
    about and return ``None`` when there is nothing to emit.
    """

    name: AudioEventBundlerName

    def bundle(self, events: list[AudioEvent]) -> FileBundle | None: ...
