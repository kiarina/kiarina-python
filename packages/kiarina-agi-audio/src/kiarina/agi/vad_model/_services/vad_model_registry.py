from typing import Any

from kiarina.utils.object_registry import ObjectRegistry

from .._models.vad_model import VADModel
from .._schemas.vad_model_config import VADModelConfig
from .._settings import settings_manager


def _configure(config: VADModelConfig, values: dict[str, Any]) -> VADModelConfig:
    config.provider_config.update(values)
    return config


vad_model_registry = ObjectRegistry[VADModel, VADModelConfig](
    expected_type=VADModel,
    object_label="VADModel",
    get_default=lambda: settings_manager.settings.default,
    get_aliases=lambda: settings_manager.settings.aliases,
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    configure=_configure,
    factory=lambda name, config: VADModel(name, config),
)
