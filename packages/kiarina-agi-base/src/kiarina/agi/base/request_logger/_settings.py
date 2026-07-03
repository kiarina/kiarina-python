from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.utils.common import ImportPath

from ._types.request_logger_name import RequestLoggerName
from ._types.request_logger_specifier import RequestLoggerSpecifier


class RequestLoggerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_REQUEST_LOGGER_",
        extra="ignore",
    )

    default: RequestLoggerSpecifier = "null"

    presets: dict[RequestLoggerName, ImportPath] = Field(
        default_factory=lambda: {
            "console": "kiarina.agi.base.request_logger_impl.console:ConsoleRequestLogger",
            "local": "kiarina.agi.base.request_logger_impl.local:LocalRequestLogger",
            "null": "kiarina.agi.base.request_logger_impl.null:NullRequestLogger",
        }
    )

    customs: dict[RequestLoggerName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(RequestLoggerSettings)
