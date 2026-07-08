from typing import Any

from kiarina.agi.run_context import RunContext
from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry

from .._settings import settings_manager
from .._types.audio_consumer import AudioConsumer


def _factory_wrapper(
    factory: ComponentFactory[AudioConsumer[Any]],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> AudioConsumer[Any]:
    run_context = kwargs.pop("run_context", None)

    if not isinstance(run_context, RunContext):
        raise ValueError("run_context must be set.")

    instance = factory(*args, **kwargs)
    instance.name = component_name
    instance.run_context = run_context

    return instance


audio_consumer_registry = ComponentRegistry[AudioConsumer[Any]](
    expected_type=AudioConsumer,
    component_label="AudioConsumer",
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)
