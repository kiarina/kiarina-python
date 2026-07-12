from typing import Any

from kiarina.utils.object_registry import ObjectRegistry

from .._models.ocr_model import OCRModel
from .._schemas.ocr_model_config import OCRModelConfig
from .._settings import settings_manager


def _configure(config: OCRModelConfig, values: dict[str, Any]) -> OCRModelConfig:
    config.provider_config.update(values)
    return config


ocr_model_registry = ObjectRegistry[OCRModel, OCRModelConfig](
    expected_type=OCRModel,
    object_label="OCRModel",
    get_default=lambda: settings_manager.settings.default,
    get_aliases=lambda: settings_manager.settings.aliases,
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    configure=_configure,
    factory=lambda name, config: OCRModel(name, config),
)
