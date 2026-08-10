from typing import Any

from .._models.siglip2_image_embedding_provider import SigLIP2ImageEmbeddingProvider
from .._settings import SigLIP2ImageEmbeddingProviderSettings, settings_manager


def create_siglip2_image_embedding_provider(
    **kwargs: Any,
) -> SigLIP2ImageEmbeddingProvider:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = SigLIP2ImageEmbeddingProviderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return SigLIP2ImageEmbeddingProvider(settings)
