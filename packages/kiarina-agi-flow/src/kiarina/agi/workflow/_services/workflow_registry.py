from typing import Any

from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._settings import settings_manager
from .._types.workflow import Workflow


def _factory_wrapper(
    factory: ComponentFactory[Workflow],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> Workflow:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance


workflow_registry = ComponentRegistry[Workflow](
    expected_type=Workflow,
    component_label="Workflow",
    get_default=lambda: settings_manager.settings.default,
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
