from typing import Any

from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._settings import settings_manager
from .._types.vad_provider import VADProvider


def _factory_wrapper(
    factory: ComponentFactory[VADProvider],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> VADProvider:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance


vad_provider_registry = ComponentRegistry[VADProvider](
    expected_type=VADProvider,
    component_label="VADProvider",
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
