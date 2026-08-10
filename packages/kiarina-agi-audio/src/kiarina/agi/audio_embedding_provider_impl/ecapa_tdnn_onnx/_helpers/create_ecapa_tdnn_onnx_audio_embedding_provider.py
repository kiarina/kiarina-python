from typing import Any

from .._models.ecapa_tdnn_onnx_audio_embedding_provider import (
    EcapaTDNNOnnxAudioEmbeddingProvider,
)
from .._settings import (
    EcapaTDNNOnnxAudioEmbeddingProviderSettings,
    settings_manager,
)


def create_ecapa_tdnn_onnx_audio_embedding_provider(
    **kwargs: Any,
) -> EcapaTDNNOnnxAudioEmbeddingProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = EcapaTDNNOnnxAudioEmbeddingProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return EcapaTDNNOnnxAudioEmbeddingProvider(settings)
