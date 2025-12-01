from pydantic import SecretStr
from pydantic_settings import BaseSettings
from pydantic_settings_manager import SettingsManager


class OpenAISettings(BaseSettings):
    api_key: SecretStr
    """OpenAI API key"""

    organization_id: str | None = None
    """OpenAI organization ID"""

    base_url: str | None = None
    """Custom base URL for OpenAI API"""


settings_manager = SettingsManager(OpenAISettings, multi=True)
