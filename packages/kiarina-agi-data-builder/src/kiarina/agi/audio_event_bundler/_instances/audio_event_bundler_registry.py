from typing import Any

from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._settings import settings_manager
from .._types.audio_event_bundler import AudioEventBundler


def _factory_wrapper(
    factory: ComponentFactory[AudioEventBundler],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> AudioEventBundler:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance


audio_event_bundler_registry = ComponentRegistry[AudioEventBundler](
    expected_type=AudioEventBundler,
    component_label="AudioEventBundler",
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
