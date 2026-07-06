from typing import TypeAlias

from .image_embedding_model_alias import ImageEmbeddingModelAlias
from .image_embedding_model_name import ImageEmbeddingModelName

ImageEmbeddingModelSpecifier: TypeAlias = (
    ImageEmbeddingModelName | ImageEmbeddingModelAlias | str
)
"""
A string in one of the following formats:

- {ImageEmbeddingModelName}
- {ImageEmbeddingModelName}?{ConfigString}
- {ImageEmbeddingModelAlias}
- {ImageEmbeddingModelAlias}?{ConfigString}
"""
