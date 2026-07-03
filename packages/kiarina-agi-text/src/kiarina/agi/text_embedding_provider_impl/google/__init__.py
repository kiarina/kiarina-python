from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_google_text_embedding_provider import (
        create_google_text_embedding_provider,
    )
    from ._models.google_text_embedding_provider import GoogleTextEmbeddingProvider
    from ._settings import GoogleTextEmbeddingProviderSettings, settings_manager

__all__ = [
    "create_google_text_embedding_provider",
    "GoogleTextEmbeddingProvider",
    "GoogleTextEmbeddingProviderSettings",
    "settings_manager",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        "create_google_text_embedding_provider": "._helpers.create_google_text_embedding_provider",
        "GoogleTextEmbeddingProvider": "._models.google_text_embedding_provider",
        "GoogleTextEmbeddingProviderSettings": "._settings",
        "settings_manager": "._settings",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
