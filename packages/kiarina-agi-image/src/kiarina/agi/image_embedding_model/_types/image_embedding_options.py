from typing import TypedDict

from .._models.image_embedding_model import ImageEmbeddingModel
from .image_embedding_model_specifier import ImageEmbeddingModelSpecifier


class ImageEmbeddingOptions(TypedDict, total=False):
    image_embedding_model: ImageEmbeddingModel | ImageEmbeddingModelSpecifier | None
