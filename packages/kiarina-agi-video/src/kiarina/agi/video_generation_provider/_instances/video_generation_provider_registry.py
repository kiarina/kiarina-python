from typing import Any

from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._settings import settings_manager
from .._types.video_generation_provider import VideoGenerationProvider


def _factory_wrapper(
    factory: ComponentFactory[VideoGenerationProvider],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> VideoGenerationProvider:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance


video_generation_provider_registry = ComponentRegistry[VideoGenerationProvider](
    expected_type=VideoGenerationProvider,
    component_label="VideoGenerationProvider",
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
