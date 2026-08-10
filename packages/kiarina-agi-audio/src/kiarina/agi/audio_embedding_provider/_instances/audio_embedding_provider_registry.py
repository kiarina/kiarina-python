from typing import Any

from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._settings import settings_manager
from .._types.audio_embedding_provider import AudioEmbeddingProvider


def _factory_wrapper(
    factory: ComponentFactory[AudioEmbeddingProvider],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> AudioEmbeddingProvider:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance


audio_embedding_provider_registry = ComponentRegistry[AudioEmbeddingProvider](
    expected_type=AudioEmbeddingProvider,
    component_label="AudioEmbeddingProvider",
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
