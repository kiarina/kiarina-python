from typing import Any

from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._settings import settings_manager
from .._types.post_hook import PostHook


def _factory_wrapper(
    factory: ComponentFactory[PostHook],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> PostHook:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance


post_hook_registry = ComponentRegistry[PostHook](
    expected_type=PostHook,
    component_label="PostHook",
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
