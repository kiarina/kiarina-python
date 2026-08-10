from typing import Any

from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._settings import settings_manager
from .._types.chat_logger import ChatLogger


def _factory_wrapper(
    factory: ComponentFactory[ChatLogger],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> ChatLogger:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance


chat_logger_registry = ComponentRegistry[ChatLogger](
    expected_type=ChatLogger,
    component_label="ChatLogger",
    get_default=lambda: settings_manager.settings.default,
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
