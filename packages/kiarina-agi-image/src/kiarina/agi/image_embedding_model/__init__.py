from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.embed_image import embed_image
    from ._instances.image_embedding_model_registry import (
        image_embedding_model_registry,
    )
    from ._models.image_embedding_model import ImageEmbeddingModel
    from ._schemas.image_embedding_model_config import ImageEmbeddingModelConfig
    from ._settings import ImageEmbeddingModelSettings, settings_manager
    from ._types.image_embedding_model_alias import ImageEmbeddingModelAlias
    from ._types.image_embedding_model_name import ImageEmbeddingModelName
    from ._types.image_embedding_model_specifier import ImageEmbeddingModelSpecifier
    from ._types.image_embedding_options import ImageEmbeddingOptions

__all__ = [
    # ._helpers
    "embed_image",
    # ._instances
    "image_embedding_model_registry",
    # ._models
    "ImageEmbeddingModel",
    # ._schemas
    "ImageEmbeddingModelConfig",
    # ._settings
    "ImageEmbeddingModelSettings",
    "settings_manager",
    # ._types
    "ImageEmbeddingModelAlias",
    "ImageEmbeddingModelName",
    "ImageEmbeddingModelSpecifier",
    "ImageEmbeddingOptions",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._helpers
        "embed_image": "._helpers.embed_image",
        # ._instances
        "image_embedding_model_registry": "._instances.image_embedding_model_registry",
        # ._models
        "ImageEmbeddingModel": "._models.image_embedding_model",
        # ._schemas
        "ImageEmbeddingModelConfig": "._schemas.image_embedding_model_config",
        # ._settings
        "ImageEmbeddingModelSettings": "._settings",
        "settings_manager": "._settings",
        # ._types
        "ImageEmbeddingModelAlias": "._types.image_embedding_model_alias",
        "ImageEmbeddingModelName": "._types.image_embedding_model_name",
        "ImageEmbeddingModelSpecifier": "._types.image_embedding_model_specifier",
        "ImageEmbeddingOptions": "._types.image_embedding_options",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
