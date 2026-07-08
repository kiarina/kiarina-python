from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.embed_audio import embed_audio
    from ._instances.audio_embedding_model_registry import (
        audio_embedding_model_registry,
    )
    from ._models.audio_embedding_model import AudioEmbeddingModel
    from ._schemas.audio_embedding_model_config import AudioEmbeddingModelConfig
    from ._settings import AudioEmbeddingModelSettings, settings_manager
    from ._types.audio_embedding_model_alias import AudioEmbeddingModelAlias
    from ._types.audio_embedding_model_name import AudioEmbeddingModelName
    from ._types.audio_embedding_model_specifier import AudioEmbeddingModelSpecifier
    from ._types.audio_embedding_options import AudioEmbeddingOptions

__all__ = [
    # ._helpers
    "embed_audio",
    # ._models
    "AudioEmbeddingModel",
    # ._schemas
    "AudioEmbeddingModelConfig",
    # ._instances
    "audio_embedding_model_registry",
    # ._settings
    "AudioEmbeddingModelSettings",
    "settings_manager",
    # ._types
    "AudioEmbeddingModelAlias",
    "AudioEmbeddingModelName",
    "AudioEmbeddingModelSpecifier",
    "AudioEmbeddingOptions",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._helpers
        "embed_audio": "._helpers.embed_audio",
        # ._models
        "AudioEmbeddingModel": "._models.audio_embedding_model",
        # ._schemas
        "AudioEmbeddingModelConfig": "._schemas.audio_embedding_model_config",
        # ._instances
        "audio_embedding_model_registry": "._instances.audio_embedding_model_registry",
        # ._settings
        "AudioEmbeddingModelSettings": "._settings",
        "settings_manager": "._settings",
        # ._types
        "AudioEmbeddingModelAlias": "._types.audio_embedding_model_alias",
        "AudioEmbeddingModelName": "._types.audio_embedding_model_name",
        "AudioEmbeddingModelSpecifier": "._types.audio_embedding_model_specifier",
        "AudioEmbeddingOptions": "._types.audio_embedding_options",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
