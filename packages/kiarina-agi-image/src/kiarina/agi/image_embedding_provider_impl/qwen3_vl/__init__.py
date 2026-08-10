from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.create_qwen3_vl_image_embedding_provider import (
        create_qwen3_vl_image_embedding_provider,
    )
    from ._models.qwen3_vl_image_embedding_provider import (
        Qwen3VLImageEmbeddingProvider,
    )
    from ._settings import Qwen3VLImageEmbeddingProviderSettings, settings_manager

__all__ = [
    "create_qwen3_vl_image_embedding_provider",
    "Qwen3VLImageEmbeddingProvider",
    "Qwen3VLImageEmbeddingProviderSettings",
    "settings_manager",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        "create_qwen3_vl_image_embedding_provider": "._helpers.create_qwen3_vl_image_embedding_provider",
        "Qwen3VLImageEmbeddingProvider": "._models.qwen3_vl_image_embedding_provider",
        "Qwen3VLImageEmbeddingProviderSettings": "._settings",
        "settings_manager": "._settings",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
