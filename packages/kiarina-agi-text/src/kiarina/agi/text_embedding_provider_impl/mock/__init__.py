from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_mock_text_embedding_provider import (
        create_mock_text_embedding_provider,
    )
    from ._models.mock_text_embedding_provider import MockTextEmbeddingProvider
    from ._settings import MockTextEmbeddingProviderSettings, settings_manager

__all__ = [
    "create_mock_text_embedding_provider",
    "MockTextEmbeddingProvider",
    "MockTextEmbeddingProviderSettings",
    "settings_manager",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        "create_mock_text_embedding_provider": "._helpers.create_mock_text_embedding_provider",
        "MockTextEmbeddingProvider": "._models.mock_text_embedding_provider",
        "MockTextEmbeddingProviderSettings": "._settings",
        "settings_manager": "._settings",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
