from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class FrankfurterRateProviderSettings(BaseSettings):
    """Frankfurter API settings."""

    model_config = SettingsConfigDict(
        env_prefix="KIARINA_CURRENCY_RATE_PROVIDER_IMPL_FRANKFURTER_",
    )

    base_url: str = Field(
        default="https://api.frankfurter.app",
        title="Base URL",
        description="Base URL of the Frankfurter API.",
    )
    timeout: float = Field(
        default=10.0,
        title="Timeout",
        description="Request timeout in seconds.",
    )


settings_manager = SettingsManager(FrankfurterRateProviderSettings)
