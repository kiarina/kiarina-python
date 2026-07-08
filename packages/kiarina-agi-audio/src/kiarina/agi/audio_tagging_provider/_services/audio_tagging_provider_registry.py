from typing import Any

from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._settings import settings_manager
from .._types.audio_tagging_provider import AudioTaggingProvider


def _factory_wrapper(
    factory: ComponentFactory[AudioTaggingProvider],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> AudioTaggingProvider:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance


audio_tagging_provider_registry = ComponentRegistry[AudioTaggingProvider](
    expected_type=AudioTaggingProvider,
    component_label="AudioTaggingProvider",
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
