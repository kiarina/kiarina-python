from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.utils.common import ImportPath

from ._types.rate_provider_name import RateProviderName


class RateProviderSettings(BaseSettings):
    """Rate provider selection settings."""

    model_config = SettingsConfigDict(
        env_prefix="KIARINA_CURRENCY_RATE_PROVIDER_",
    )

    default: RateProviderName = Field(
        default="static",
        title="Default Provider",
        description="Provider used when no provider is specified.",
    )

    providers: dict[RateProviderName, ImportPath] = Field(
        default={
            "frankfurter": "kiarina.currency.rate_provider_impl.frankfurter:FrankfurterRateProvider",
            "static": "kiarina.currency.rate_provider_impl.static:StaticRateProvider",
        },
        title="Providers",
        description="Import paths keyed by provider name.",
    )


settings_manager = SettingsManager(RateProviderSettings)
