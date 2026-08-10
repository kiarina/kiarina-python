from typing import Any

from kiarina.utils.object_registry import ObjectRegistry

from .._models.asr_model import ASRModel
from .._schemas.asr_model_config import ASRModelConfig
from .._settings import settings_manager


def _configure(config: ASRModelConfig, values: dict[str, Any]) -> ASRModelConfig:
    config.provider_config.update(values)
    return config


asr_model_registry = ObjectRegistry[ASRModel, ASRModelConfig](
    expected_type=ASRModel,
    object_label="ASRModel",
    get_default=lambda: settings_manager.settings.default,
    get_aliases=lambda: settings_manager.settings.aliases,
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    configure=_configure,
    factory=lambda name, config: ASRModel(name, config),
)
