from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_gemini_image_embedding_provider import (
        create_gemini_image_embedding_provider,
    )
    from ._models.gemini_image_embedding_provider import GeminiImageEmbeddingProvider
    from ._settings import GeminiImageEmbeddingProviderSettings, settings_manager

__all__ = [
    "create_gemini_image_embedding_provider",
    "GeminiImageEmbeddingProvider",
    "GeminiImageEmbeddingProviderSettings",
    "settings_manager",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        "create_gemini_image_embedding_provider": "._helpers.create_gemini_image_embedding_provider",
        "GeminiImageEmbeddingProvider": "._models.gemini_image_embedding_provider",
        "GeminiImageEmbeddingProviderSettings": "._settings",
        "settings_manager": "._settings",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
