from typing import TypedDict

from .._models.audio_embedding_model import AudioEmbeddingModel
from .audio_embedding_model_specifier import AudioEmbeddingModelSpecifier


class AudioEmbeddingOptions(TypedDict, total=False):
    audio_embedding_model: AudioEmbeddingModel | AudioEmbeddingModelSpecifier | None
