from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class SlackSettings(BaseSettings):
    """Slack app settings."""

    model_config = SettingsConfigDict(
        env_prefix="KIARINA_LIB_SLACK_",
        extra="ignore",
    )

    app_id: str = Field(
        title="App ID",
        description="Slack app ID.",
    )

    client_id: str = Field(
        title="Client ID",
        description="Slack OAuth client ID.",
    )

    client_secret: SecretStr = Field(
        title="Client Secret",
        description="Slack OAuth client secret.",
    )

    signing_secret: SecretStr = Field(
        title="Signing Secret",
        description="Slack request signing secret.",
    )

    app_token: SecretStr | None = Field(
        default=None,
        title="App Token",
        description="Slack app-level token for Socket Mode.",
    )

    scopes: list[str] = Field(
        default_factory=list,
        title="OAuth Scopes",
        description="OAuth scopes requested by the Slack app.",
    )

    team_id: str | None = Field(
        default=None,
        title="Team ID",
        description="Slack workspace ID.",
    )

    enterprise_id: str | None = Field(
        default=None,
        title="Enterprise ID",
        description="Slack Enterprise Grid organization ID.",
    )

    bot_token: SecretStr | None = Field(
        default=None,
        title="Bot Token",
        description="Slack bot user OAuth token.",
    )


settings_manager = SettingsManager(SlackSettings, multi=True)
"""Manager for named Slack app settings."""
