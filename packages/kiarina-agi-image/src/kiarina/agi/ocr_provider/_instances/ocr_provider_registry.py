from typing import Any

from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._settings import settings_manager
from .._types.ocr_provider import OCRProvider


def _factory_wrapper(
    factory: ComponentFactory[OCRProvider],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> OCRProvider:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance


ocr_provider_registry = ComponentRegistry[OCRProvider](
    expected_type=OCRProvider,
    component_label="OCRProvider",
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
