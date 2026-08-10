from typing import Any

from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._settings import settings_manager
from .._types.cost_logger import CostLogger


def _factory_wrapper(
    factory: ComponentFactory[CostLogger],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> CostLogger:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance


cost_logger_registry = ComponentRegistry[CostLogger](
    expected_type=CostLogger,
    component_label="CostLogger",
    get_default=lambda: settings_manager.settings.default,
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
