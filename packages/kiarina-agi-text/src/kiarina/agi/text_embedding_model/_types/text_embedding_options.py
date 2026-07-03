from typing import TypedDict

from .._models.text_embedding_model import TextEmbeddingModel
from .text_embedding_model_specifier import TextEmbeddingModelSpecifier


class TextEmbeddingOptions(TypedDict, total=False):
    text_embedding_model: TextEmbeddingModel | TextEmbeddingModelSpecifier | None
