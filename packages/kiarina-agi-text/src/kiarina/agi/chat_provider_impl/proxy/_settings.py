from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class ProxyChatProviderSettings(BaseSettings):
    """
    Sends requests to a chat proxy (`kiarina.agi.chat_proxy`), which runs them on
    one of its chat models. The capabilities are the proxy's chat model's, read
    from the proxy once.
    """

    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_CHAT_PROVIDER_IMPL_PROXY_",
        extra="ignore",
    )

    base_url: str = Field(
        default="http://127.0.0.1:8795",
        title="Base URL",
        description="The chat proxy's URL.",
    )
    model_name: str = Field(
        default="codex",
        title="Model Name",
        description="The chat model name or alias on the chat proxy.",
    )
    token: SecretStr | None = Field(
        default=None,
        title="Token",
        description="The bearer token for the chat proxy.",
    )
    timeout: float | None = Field(
        default=900.0,
        title="Timeout",
        description="Seconds to wait for each read from the chat proxy.",
    )


settings_manager = SettingsManager(ProxyChatProviderSettings)
