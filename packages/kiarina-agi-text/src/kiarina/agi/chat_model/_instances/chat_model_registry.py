from typing import Any

from kiarina.utils.object_registry import ObjectRegistry

from .._models.chat_model import ChatModel
from .._schemas.chat_model_config import ChatModelConfig
from .._settings import settings_manager


def _configure(config: ChatModelConfig, values: dict[str, Any]) -> ChatModelConfig:
    config.provider_config.update(values)
    return config


chat_model_registry = ObjectRegistry[ChatModel, ChatModelConfig](
    expected_type=ChatModel,
    object_label="ChatModel",
    get_default=lambda: settings_manager.settings.default,
    get_aliases=lambda: settings_manager.settings.aliases,
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    configure=_configure,
    factory=lambda name, config: ChatModel(name, config),
)
