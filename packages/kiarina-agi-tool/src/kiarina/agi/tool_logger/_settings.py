from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.utils.common import ImportPath

from ._types.tool_logger_name import ToolLoggerName
from ._types.tool_logger_specifier import ToolLoggerSpecifier


class ToolLoggerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_TOOL_LOGGER_",
        extra="ignore",
    )

    default: ToolLoggerSpecifier = "null"

    presets: dict[ToolLoggerName, ImportPath] = Field(
        default_factory=lambda: {
            "console": "kiarina.agi.tool_logger_impl.console:ConsoleToolLogger",
            "null": "kiarina.agi.tool_logger_impl.null:NullToolLogger",
        }
    )

    customs: dict[ToolLoggerName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(ToolLoggerSettings)
