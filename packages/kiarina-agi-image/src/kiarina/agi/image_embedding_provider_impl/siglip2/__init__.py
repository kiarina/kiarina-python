from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_siglip2_image_embedding_provider import (
        create_siglip2_image_embedding_provider,
    )
    from ._models.siglip2_image_embedding_provider import (
        SigLIP2ImageEmbeddingProvider,
    )
    from ._settings import SigLIP2ImageEmbeddingProviderSettings, settings_manager

__all__ = [
    "create_siglip2_image_embedding_provider",
    "SigLIP2ImageEmbeddingProvider",
    "SigLIP2ImageEmbeddingProviderSettings",
    "settings_manager",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        "create_siglip2_image_embedding_provider": "._helpers.create_siglip2_image_embedding_provider",
        "SigLIP2ImageEmbeddingProvider": "._models.siglip2_image_embedding_provider",
        "SigLIP2ImageEmbeddingProviderSettings": "._settings",
        "settings_manager": "._settings",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
