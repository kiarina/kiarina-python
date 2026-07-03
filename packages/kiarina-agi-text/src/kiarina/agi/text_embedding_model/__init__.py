from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.embed_text import embed_text
    from ._models.text_embedding_model import TextEmbeddingModel
    from ._schemas.text_embedding_model_config import TextEmbeddingModelConfig
    from ._services.text_embedding_model_registry import text_embedding_model_registry
    from ._settings import TextEmbeddingModelSettings, settings_manager
    from ._types.text_embedding_model_alias import TextEmbeddingModelAlias
    from ._types.text_embedding_model_name import TextEmbeddingModelName
    from ._types.text_embedding_model_specifier import TextEmbeddingModelSpecifier
    from ._types.text_embedding_options import TextEmbeddingOptions

__all__ = [
    "embed_text",
    "TextEmbeddingModel",
    "TextEmbeddingModelConfig",
    "text_embedding_model_registry",
    "TextEmbeddingModelSettings",
    "settings_manager",
    "TextEmbeddingModelAlias",
    "TextEmbeddingModelName",
    "TextEmbeddingModelSpecifier",
    "TextEmbeddingOptions",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        "embed_text": "._helpers.embed_text",
        "TextEmbeddingModel": "._models.text_embedding_model",
        "TextEmbeddingModelConfig": "._schemas.text_embedding_model_config",
        "text_embedding_model_registry": "._services.text_embedding_model_registry",
        "TextEmbeddingModelSettings": "._settings",
        "settings_manager": "._settings",
        "TextEmbeddingModelAlias": "._types.text_embedding_model_alias",
        "TextEmbeddingModelName": "._types.text_embedding_model_name",
        "TextEmbeddingModelSpecifier": "._types.text_embedding_model_specifier",
        "TextEmbeddingOptions": "._types.text_embedding_options",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
