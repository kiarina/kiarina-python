from typing import Any

from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._settings import settings_manager
from .._types.agent import Agent


def _factory_wrapper(
    factory: ComponentFactory[Agent],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> Agent:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance


agent_registry = ComponentRegistry[Agent](
    expected_type=Agent,
    component_label="Agent",
    get_default=lambda: settings_manager.settings.default,
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
