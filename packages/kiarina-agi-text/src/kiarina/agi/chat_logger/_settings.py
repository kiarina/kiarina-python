from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.utils.common import ImportPath

from ._types.chat_logger_name import ChatLoggerName
from ._types.chat_logger_specifier import ChatLoggerSpecifier


class ChatLoggerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_CHAT_LOGGER_",
        extra="ignore",
    )

    default: ChatLoggerSpecifier = "null"

    presets: dict[ChatLoggerName, ImportPath] = Field(
        default_factory=lambda: {
            "console": "kiarina.agi.chat_logger_impl.console:ConsoleChatLogger",
            "null": "kiarina.agi.chat_logger_impl.null:NullChatLogger",
        }
    )

    customs: dict[ChatLoggerName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(ChatLoggerSettings)
