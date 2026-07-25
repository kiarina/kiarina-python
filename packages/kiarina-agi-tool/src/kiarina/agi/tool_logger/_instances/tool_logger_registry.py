from typing import Any

from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._settings import settings_manager
from .._types.tool_logger import ToolLogger


def _factory_wrapper(
    factory: ComponentFactory[ToolLogger],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> ToolLogger:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance


tool_logger_registry = ComponentRegistry[ToolLogger](
    expected_type=ToolLogger,
    component_label="ToolLogger",
    get_default=lambda: settings_manager.settings.default,
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
