from typing import Any

from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._settings import settings_manager
from .._types.scd_provider import SCDProvider


def _factory_wrapper(
    factory: ComponentFactory[SCDProvider],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> SCDProvider:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance


scd_provider_registry = ComponentRegistry[SCDProvider](
    expected_type=SCDProvider,
    component_label="SCDProvider",
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
