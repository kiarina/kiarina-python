from typing import Any

from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._settings import settings_manager
from .._types.image_detection_provider import ImageDetectionProvider


def _factory_wrapper(
    factory: ComponentFactory[ImageDetectionProvider],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> ImageDetectionProvider:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance


image_detection_provider_registry = ComponentRegistry[ImageDetectionProvider](
    expected_type=ImageDetectionProvider,
    component_label="ImageDetectionProvider",
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
