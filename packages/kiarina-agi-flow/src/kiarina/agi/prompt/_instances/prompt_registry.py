from typing import Any

from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._settings import settings_manager
from .._types.prompt import Prompt


def _factory_wrapper(
    factory: ComponentFactory[Prompt],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> Prompt:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance


prompt_registry = ComponentRegistry[Prompt](
    expected_type=Prompt,
    component_label="Prompt",
    get_default=lambda: settings_manager.settings.default,
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
