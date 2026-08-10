from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_stt_audio_consumer import create_stt_audio_consumer
    from ._models.stt_audio_consumer import STTAudioConsumer
    from ._schemas.stt_audio_event import STTAudioEvent
    from ._settings import STTAudioConsumerSettings, settings_manager

__all__ = [
    # ._helpers
    "create_stt_audio_consumer",
    # ._models
    "STTAudioConsumer",
    # ._schemas
    "STTAudioEvent",
    # ._settings
    "STTAudioConsumerSettings",
    "settings_manager",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._helpers
        "create_stt_audio_consumer": "._helpers.create_stt_audio_consumer",
        # ._models
        "STTAudioConsumer": "._models.stt_audio_consumer",
        # ._schemas
        "STTAudioEvent": "._schemas.stt_audio_event",
        # ._settings
        "STTAudioConsumerSettings": "._settings",
        "settings_manager": "._settings",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
