from typing import Any

from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._settings import settings_manager
from .._types.image_segmentation_provider import ImageSegmentationProvider


def _factory_wrapper(
    factory: ComponentFactory[ImageSegmentationProvider],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> ImageSegmentationProvider:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance


image_segmentation_provider_registry = ComponentRegistry[ImageSegmentationProvider](
    expected_type=ImageSegmentationProvider,
    component_label="ImageSegmentationProvider",
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
