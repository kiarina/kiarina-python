from typing import Any

from .._models.sface_image_embedding_provider import SFaceImageEmbeddingProvider
from .._settings import SFaceImageEmbeddingProviderSettings, settings_manager


def create_sface_image_embedding_provider(
    **kwargs: Any,
) -> SFaceImageEmbeddingProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = SFaceImageEmbeddingProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return SFaceImageEmbeddingProvider(settings)
