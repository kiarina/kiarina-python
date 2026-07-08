from typing import Any

from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._settings import settings_manager
from .._types.text_embedding_provider import TextEmbeddingProvider


def _factory_wrapper(
    factory: ComponentFactory[TextEmbeddingProvider],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> TextEmbeddingProvider:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance


text_embedding_provider_registry = ComponentRegistry[TextEmbeddingProvider](
    expected_type=TextEmbeddingProvider,
    component_label="TextEmbeddingProvider",
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
