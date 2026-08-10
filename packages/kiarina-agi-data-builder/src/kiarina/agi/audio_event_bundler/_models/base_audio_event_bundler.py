from .._types.audio_event_bundler import AudioEventBundler
from .._types.audio_event_bundler_name import AudioEventBundlerName


class BaseAudioEventBundler(AudioEventBundler):
    def __init__(self) -> None:
        self._name: AudioEventBundlerName | None = None

    @property
    def name(self) -> AudioEventBundlerName:
        if self._name is None:  # pragma: no cover
            raise ValueError("AudioEventBundler name is not set.")

        return self._name

    @name.setter
    def name(self, value: AudioEventBundlerName) -> None:
        self._name = value

    def __str__(self) -> str:
        return self.__class__.__name__
