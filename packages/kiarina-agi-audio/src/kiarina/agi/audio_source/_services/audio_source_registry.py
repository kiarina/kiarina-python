from typing import Any

from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._settings import settings_manager
from .._types.audio_source import AudioSource


def _factory_wrapper(
    factory: ComponentFactory[AudioSource],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> AudioSource:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance


audio_source_registry = ComponentRegistry[AudioSource](
    expected_type=AudioSource,
    component_label="AudioSource",
    get_default=lambda: settings_manager.settings.default,
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
