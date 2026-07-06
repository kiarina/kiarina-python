from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_sface_image_embedding_provider import (
        create_sface_image_embedding_provider,
    )
    from ._models.sface_image_embedding_provider import SFaceImageEmbeddingProvider
    from ._settings import SFaceImageEmbeddingProviderSettings, settings_manager

__all__ = [
    "create_sface_image_embedding_provider",
    "SFaceImageEmbeddingProvider",
    "SFaceImageEmbeddingProviderSettings",
    "settings_manager",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        "create_sface_image_embedding_provider": "._helpers.create_sface_image_embedding_provider",
        "SFaceImageEmbeddingProvider": "._models.sface_image_embedding_provider",
        "SFaceImageEmbeddingProviderSettings": "._settings",
        "settings_manager": "._settings",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
