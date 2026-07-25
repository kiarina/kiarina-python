from typing import Any

from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._settings import settings_manager
from .._types.tool import Tool


def _factory_wrapper(
    factory: ComponentFactory[Tool],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> Tool:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance


tool_registry = ComponentRegistry[Tool](
    expected_type=Tool,
    component_label="Tool",
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
