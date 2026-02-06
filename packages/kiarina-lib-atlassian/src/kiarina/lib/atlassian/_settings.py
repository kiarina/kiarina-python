from pydantic import SecretStr
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class AtlassianSettings(BaseSettings):

    model_config = SettingsConfigDict(
        env_prefix="KIARINA_LIB_ATLASSIAN_",
        extra="ignore",
    )

    url: str = ""
    """API endpoint URL (e.g., "https://your-domain.atlassian.net")"""

    username: str = ""
    """Atlassian account email address"""

    password: SecretStr = Field(default_factory=lambda: SecretStr(""))
    """Atlassian API token (stored securely using SecretStr)"""


settings_manager = SettingsManager(AtlassianSettings, multi=True)
