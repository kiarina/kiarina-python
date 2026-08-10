from typing import Any

from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._settings import settings_manager
from .._types.video_source import VideoSource


def _factory_wrapper(
    factory: ComponentFactory[VideoSource],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> VideoSource:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance


video_source_registry = ComponentRegistry[VideoSource](
    expected_type=VideoSource,
    component_label="VideoSource",
    get_default=lambda: settings_manager.settings.default,
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
