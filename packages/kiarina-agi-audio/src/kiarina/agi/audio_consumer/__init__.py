from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._models.base_audio_consumer import BaseAudioConsumer
    from ._schemas.audio_event import AudioEvent
    from ._services.audio_consumer_registry import audio_consumer_registry
    from ._settings import AudioConsumerSettings, settings_manager
    from ._types.audio_consumer import AudioConsumer
    from ._types.audio_consumer_name import AudioConsumerName
    from ._types.audio_consumer_specifier import AudioConsumerSpecifier

__all__ = [
    # ._models
    "BaseAudioConsumer",
    # ._schemas
    "AudioEvent",
    # ._services
    "audio_consumer_registry",
    # ._settings
    "AudioConsumerSettings",
    "settings_manager",
    # ._types
    "AudioConsumer",
    "AudioConsumerName",
    "AudioConsumerSpecifier",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._models
        "BaseAudioConsumer": "._models.base_audio_consumer",
        # ._schemas
        "AudioEvent": "._schemas.audio_event",
        # ._services
        "audio_consumer_registry": "._services.audio_consumer_registry",
        # ._settings
        "AudioConsumerSettings": "._settings",
        "settings_manager": "._settings",
        # ._types
        "AudioConsumer": "._types.audio_consumer",
        "AudioConsumerName": "._types.audio_consumer_name",
        "AudioConsumerSpecifier": "._types.audio_consumer_specifier",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
