from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._instances.image_embedding_provider_registry import (
        image_embedding_provider_registry,
    )
    from ._models.base_image_embedding_provider import BaseImageEmbeddingProvider
    from ._settings import ImageEmbeddingProviderSettings, settings_manager
    from ._types.image_embedding_provider import ImageEmbeddingProvider
    from ._types.image_embedding_provider_name import ImageEmbeddingProviderName

__all__ = [
    # ._instances
    "image_embedding_provider_registry",
    # ._models
    "BaseImageEmbeddingProvider",
    # ._settings
    "ImageEmbeddingProviderSettings",
    "settings_manager",
    # ._types
    "ImageEmbeddingProvider",
    "ImageEmbeddingProviderName",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._instances
        "image_embedding_provider_registry": "._instances.image_embedding_provider_registry",
        # ._models
        "BaseImageEmbeddingProvider": "._models.base_image_embedding_provider",
        # ._settings
        "ImageEmbeddingProviderSettings": "._settings",
        "settings_manager": "._settings",
        # ._types
        "ImageEmbeddingProvider": "._types.image_embedding_provider",
        "ImageEmbeddingProviderName": "._types.image_embedding_provider_name",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
