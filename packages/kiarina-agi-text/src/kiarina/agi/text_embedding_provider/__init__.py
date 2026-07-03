from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._models.base_text_embedding_provider import BaseTextEmbeddingProvider
    from ._services.text_embedding_provider_registry import (
        text_embedding_provider_registry,
    )
    from ._settings import TextEmbeddingProviderSettings, settings_manager
    from ._types.text_embedding_provider import TextEmbeddingProvider
    from ._types.text_embedding_provider_name import TextEmbeddingProviderName

__all__ = [
    "BaseTextEmbeddingProvider",
    "text_embedding_provider_registry",
    "TextEmbeddingProviderSettings",
    "settings_manager",
    "TextEmbeddingProvider",
    "TextEmbeddingProviderName",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        "BaseTextEmbeddingProvider": "._models.base_text_embedding_provider",
        "text_embedding_provider_registry": "._services.text_embedding_provider_registry",
        "TextEmbeddingProviderSettings": "._settings",
        "settings_manager": "._settings",
        "TextEmbeddingProvider": "._types.text_embedding_provider",
        "TextEmbeddingProviderName": "._types.text_embedding_provider_name",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
