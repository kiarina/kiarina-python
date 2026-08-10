from typing import TypeAlias

from .text_embedding_model_alias import TextEmbeddingModelAlias
from .text_embedding_model_name import TextEmbeddingModelName

TextEmbeddingModelSpecifier: TypeAlias = (
    TextEmbeddingModelName | TextEmbeddingModelAlias | str
)
"""A text embedding model name, alias, or config specifier.

Examples:
- {TextEmbeddingModelName}
- {TextEmbeddingModelName}?{ConfigString}
- {TextEmbeddingModelAlias}
- {TextEmbeddingModelAlias}?{ConfigString}
"""
