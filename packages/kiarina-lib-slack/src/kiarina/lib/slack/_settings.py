from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class SlackSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_LIB_SLACK_",
        extra="ignore",
    )

    app_id: str
    """Slack App ID"""

    client_id: str
    """Slack Client ID"""

    client_secret: SecretStr
    """Slack Client Secret"""

    signing_secret: SecretStr
    """Slack Signing Secret"""

    scopes: list[str] = Field(default_factory=list)
    """OAuth Scopes for the Slack App"""

    app_token: SecretStr | None = None
    """Slack App-Level Token (xapp-...)"""

    team_id: str | None = None
    """Slack Team ID"""

    enterprise_id: str | None = None
    """Slack Enterprise ID"""

    bot_token: SecretStr | None = None
    """Slack Bot User OAuth Token (xoxb-...)"""

    file_installation_store_base_dir: str | None = None
    """Base directory for storing Slack file installation data."""


settings_manager = SettingsManager(SlackSettings, multi=True)
