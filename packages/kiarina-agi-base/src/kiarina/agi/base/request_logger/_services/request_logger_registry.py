from typing import Any

from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._settings import settings_manager
from .._types.request_logger import RequestLogger


def _factory_wrapper(
    factory: ComponentFactory[RequestLogger],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> RequestLogger:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance


request_logger_registry = ComponentRegistry[RequestLogger](
    expected_type=RequestLogger,  # type: ignore[type-abstract]
    component_label="RequestLogger",
    get_default=lambda: settings_manager.settings.default,
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
