from typing import Any

from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._settings import settings_manager
from .._types.tts_provider import TTSProvider


def _factory_wrapper(
    factory: ComponentFactory[TTSProvider],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> TTSProvider:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance


tts_provider_registry = ComponentRegistry[TTSProvider](
    expected_type=TTSProvider,
    component_label="TTSProvider",
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
