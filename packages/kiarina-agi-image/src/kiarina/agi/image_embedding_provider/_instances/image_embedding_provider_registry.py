from typing import Any

from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._settings import settings_manager
from .._types.image_embedding_provider import ImageEmbeddingProvider


def _factory_wrapper(
    factory: ComponentFactory[ImageEmbeddingProvider],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> ImageEmbeddingProvider:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance


image_embedding_provider_registry = ComponentRegistry[ImageEmbeddingProvider](
    expected_type=ImageEmbeddingProvider,
    component_label="ImageEmbeddingProvider",
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
