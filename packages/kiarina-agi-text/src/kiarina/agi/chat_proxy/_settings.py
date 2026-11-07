from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class ChatProxySettings(BaseSettings):
    """
    The chat proxy: an HTTP server that runs requests from the `proxy` chat provider
    on its own chat models, such as `codex` and `claude_code` with this machine's
    subscription logins.
    """

    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_CHAT_PROXY_",
        extra="ignore",
    )

    host: str = Field(
        default="127.0.0.1", title="Host", description="The address to listen on."
    )
    port: int = Field(default=8795, title="Port", description="The port to listen on.")
    token: SecretStr | None = Field(
        default=None,
        title="Token",
        description="The bearer token callers must send. No check when unset.",
    )
    allowed_models: list[str] | None = Field(
        default=None,
        title="Allowed Models",
        description="Chat model names or aliases callers may use. Any when unset.",
    )
    max_concurrency: int = Field(
        default=4,
        title="Max Concurrency",
        description="Requests run at once. Later ones wait.",
    )
    cache_ttl: int = Field(
        default=86400,
        ge=0,
        title="Cache TTL",
        description=(
            "Seconds after their last use that files in the app's user cache "
            "directory are deleted. Checked at startup and hourly. 0 keeps them."
        ),
    )


settings_manager = SettingsManager(ChatProxySettings)
