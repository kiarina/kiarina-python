from typing import Any

from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._settings import settings_manager
from .._types.cost_recorder import CostRecorder


def _factory_wrapper(
    factory: ComponentFactory[CostRecorder],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> CostRecorder:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance


cost_recorder_registry = ComponentRegistry[CostRecorder](
    expected_type=CostRecorder,
    component_label="CostRecorder",
    get_default=lambda: settings_manager.settings.default,
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
