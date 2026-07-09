from typing import Any

from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._settings import settings_manager
from .._types.pre_hook import PreHook


def _factory_wrapper(
    factory: ComponentFactory[PreHook],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> PreHook:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance


pre_hook_registry = ComponentRegistry[PreHook](
    expected_type=PreHook,
    component_label="PreHook",
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
