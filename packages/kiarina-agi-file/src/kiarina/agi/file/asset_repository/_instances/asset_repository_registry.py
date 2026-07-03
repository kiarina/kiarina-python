from typing import Any

from kiarina.agi.base.run_context import RunContext
from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._schemas.uri_policy import URIPolicy
from .._settings import settings_manager
from .._types.asset_repository import AssetRepository


def _factory_wrapper(
    factory: ComponentFactory[AssetRepository],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> AssetRepository:
    uri_policy = kwargs.pop("uri_policy")
    run_context = kwargs.pop("run_context")

    if not isinstance(uri_policy, URIPolicy):
        raise ValueError("uri_policy must be a URIPolicy.")

    if not isinstance(run_context, RunContext):
        raise ValueError("run_context must be a RunContext.")

    instance = factory(*args, **kwargs)
    instance.uri_policy = uri_policy
    instance.run_context = run_context
    return instance


asset_repository_registry = ComponentRegistry[AssetRepository](
    expected_type=AssetRepository,  # type: ignore[type-abstract]
    component_label="AssetRepository",
    get_default=lambda: settings_manager.settings.default,
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
