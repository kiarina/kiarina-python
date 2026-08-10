from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_ambient_audio_consumer import create_ambient_audio_consumer
    from ._models.ambient_audio_consumer import AmbientAudioConsumer
    from ._schemas.ambient_audio_event import AmbientAudioEvent
    from ._settings import AmbientAudioConsumerSettings, settings_manager

__all__ = [
    # ._helpers
    "create_ambient_audio_consumer",
    # ._models
    "AmbientAudioConsumer",
    # ._schemas
    "AmbientAudioEvent",
    # ._settings
    "AmbientAudioConsumerSettings",
    "settings_manager",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._helpers
        "create_ambient_audio_consumer": "._helpers.create_ambient_audio_consumer",
        # ._models
        "AmbientAudioConsumer": "._models.ambient_audio_consumer",
        # ._schemas
        "AmbientAudioEvent": "._schemas.ambient_audio_event",
        # ._settings
        "AmbientAudioConsumerSettings": "._settings",
        "settings_manager": "._settings",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
