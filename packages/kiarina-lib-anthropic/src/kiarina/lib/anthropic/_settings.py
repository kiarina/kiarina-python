from pydantic import SecretStr
from pydantic_settings import BaseSettings
from pydantic_settings_manager import SettingsManager


class AnthropicSettings(BaseSettings):
    api_key: SecretStr
    """Anthropic API key"""

    base_url: str | None = None
    """Custom base URL for Anthropic API"""


settings_manager = SettingsManager(AnthropicSettings, multi=True)
