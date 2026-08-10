from typing import TypeAlias

from .audio_embedding_model_alias import AudioEmbeddingModelAlias
from .audio_embedding_model_name import AudioEmbeddingModelName

AudioEmbeddingModelSpecifier: TypeAlias = (
    AudioEmbeddingModelName | AudioEmbeddingModelAlias | str
)
"""
A string in one of the following formats:

- {AudioEmbeddingModelName}
- {AudioEmbeddingModelName}?{ConfigString}
- {AudioEmbeddingModelAlias}
- {AudioEmbeddingModelAlias}?{ConfigString}
"""
