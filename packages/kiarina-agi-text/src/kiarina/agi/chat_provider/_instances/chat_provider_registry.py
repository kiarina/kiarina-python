from typing import Any

from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._settings import settings_manager
from .._types.chat_provider import ChatProvider


def _factory_wrapper(
    factory: ComponentFactory[ChatProvider],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> ChatProvider:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance


chat_provider_registry = ComponentRegistry[ChatProvider](
    expected_type=ChatProvider,
    component_label="ChatProvider",
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
