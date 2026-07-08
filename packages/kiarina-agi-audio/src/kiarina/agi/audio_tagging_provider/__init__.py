from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._instances.audio_tagging_provider_registry import (
        audio_tagging_provider_registry,
    )
    from ._models.base_audio_tagging_provider import BaseAudioTaggingProvider
    from ._schemas.audio_tag_prediction import AudioTagPrediction
    from ._settings import AudioTaggingProviderSettings, settings_manager
    from ._types.audio_tagging_provider import AudioTaggingProvider
    from ._types.audio_tagging_provider_name import AudioTaggingProviderName

__all__ = [
    "BaseAudioTaggingProvider",
    "AudioTagPrediction",
    "audio_tagging_provider_registry",
    "AudioTaggingProviderSettings",
    "settings_manager",
    "AudioTaggingProvider",
    "AudioTaggingProviderName",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        "BaseAudioTaggingProvider": "._models.base_audio_tagging_provider",
        "AudioTagPrediction": "._schemas.audio_tag_prediction",
        "audio_tagging_provider_registry": "._instances.audio_tagging_provider_registry",
        "AudioTaggingProviderSettings": "._settings",
        "settings_manager": "._settings",
        "AudioTaggingProvider": "._types.audio_tagging_provider",
        "AudioTaggingProviderName": "._types.audio_tagging_provider_name",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
