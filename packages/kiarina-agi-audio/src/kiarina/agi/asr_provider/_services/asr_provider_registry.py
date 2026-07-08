from typing import Any

from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._settings import settings_manager
from .._types.asr_provider import ASRProvider


def _factory_wrapper(
    factory: ComponentFactory[ASRProvider],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> ASRProvider:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance


asr_provider_registry = ComponentRegistry[ASRProvider](
    expected_type=ASRProvider,
    component_label="ASRProvider",
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
