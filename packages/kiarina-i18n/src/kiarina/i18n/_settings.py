from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings_manager import SettingsManager

from ._types.language import Language


class I18nSettings(BaseSettings):
    """Internationalization settings."""

    default_language: Language = Field(
        default="en",
        title="Default Language",
        description="Language used when a translation is unavailable.",
    )


settings_manager = SettingsManager(I18nSettings)
