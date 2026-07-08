from typing import Any

from kiarina.utils.object_registry import ObjectRegistry

from .._models.tts_model import TTSModel
from .._schemas.tts_model_config import TTSModelConfig
from .._settings import settings_manager


def _configure(config: TTSModelConfig, values: dict[str, Any]) -> TTSModelConfig:
    config.provider_config.update(values)
    return config


tts_model_registry = ObjectRegistry[TTSModel, TTSModelConfig](
    expected_type=TTSModel,
    object_label="TTSModel",
    get_default=lambda: settings_manager.settings.default,
    get_aliases=lambda: settings_manager.settings.aliases,
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    configure=_configure,
    factory=lambda name, config: TTSModel(name, config),
)
