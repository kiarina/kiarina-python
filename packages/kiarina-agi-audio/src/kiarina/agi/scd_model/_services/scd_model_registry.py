from typing import Any

from kiarina.utils.object_registry import ObjectRegistry

from .._models.scd_model import SCDModel
from .._schemas.scd_model_config import SCDModelConfig
from .._settings import settings_manager


def _configure(config: SCDModelConfig, values: dict[str, Any]) -> SCDModelConfig:
    config.provider_config.update(values)
    return config


scd_model_registry = ObjectRegistry[SCDModel, SCDModelConfig](
    expected_type=SCDModel,
    object_label="SCDModel",
    get_default=lambda: settings_manager.settings.default,
    get_aliases=lambda: settings_manager.settings.aliases,
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    configure=_configure,
    factory=lambda name, config: SCDModel(name, config),
)
