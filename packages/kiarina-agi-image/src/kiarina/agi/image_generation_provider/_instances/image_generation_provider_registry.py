from typing import Any

from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._settings import settings_manager
from .._types.image_generation_provider import ImageGenerationProvider


def _factory_wrapper(
    factory: ComponentFactory[ImageGenerationProvider],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> ImageGenerationProvider:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance


image_generation_provider_registry = ComponentRegistry[ImageGenerationProvider](
    expected_type=ImageGenerationProvider,  # type: ignore[type-abstract]
    component_label="ImageGenerationProvider",
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
