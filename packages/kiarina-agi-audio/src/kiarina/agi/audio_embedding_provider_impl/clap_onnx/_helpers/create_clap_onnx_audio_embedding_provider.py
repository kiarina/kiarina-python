from typing import Any

from .._models.clap_onnx_audio_embedding_provider import ClapOnnxAudioEmbeddingProvider
from .._settings import ClapOnnxAudioEmbeddingProviderSettings, settings_manager


def create_clap_onnx_audio_embedding_provider(
    **kwargs: Any,
) -> ClapOnnxAudioEmbeddingProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = ClapOnnxAudioEmbeddingProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return ClapOnnxAudioEmbeddingProvider(settings)
