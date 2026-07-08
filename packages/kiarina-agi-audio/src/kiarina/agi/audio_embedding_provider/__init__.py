from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._instances.audio_embedding_provider_registry import (
        audio_embedding_provider_registry,
    )
    from ._models.base_audio_embedding_provider import BaseAudioEmbeddingProvider
    from ._settings import AudioEmbeddingProviderSettings, settings_manager
    from ._types.audio_embedding_provider import AudioEmbeddingProvider
    from ._types.audio_embedding_provider_name import AudioEmbeddingProviderName

__all__ = [
    # ._models
    "BaseAudioEmbeddingProvider",
    # ._instances
    "audio_embedding_provider_registry",
    # ._settings
    "AudioEmbeddingProviderSettings",
    "settings_manager",
    # ._types
    "AudioEmbeddingProvider",
    "AudioEmbeddingProviderName",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._models
        "BaseAudioEmbeddingProvider": "._models.base_audio_embedding_provider",
        # ._instances
        "audio_embedding_provider_registry": "._instances.audio_embedding_provider_registry",
        # ._settings
        "AudioEmbeddingProviderSettings": "._settings",
        "settings_manager": "._settings",
        # ._types
        "AudioEmbeddingProvider": "._types.audio_embedding_provider",
        "AudioEmbeddingProviderName": "._types.audio_embedding_provider_name",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
