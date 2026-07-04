from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.currency import CurrencyCode
from kiarina.i18n import Language

from ._types.id_str import IDStr
from ._types.time_zone import TimeZone


class RunContextSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_RUN_CONTEXT_",
        extra="ignore",
    )

    organization_id: IDStr | None = "default"

    user_id: IDStr | None = "default"

    agent_id: IDStr | None = "default"

    node_id: IDStr | None = "default"

    disallow_default_ids: bool = Field(
        default=False,
        title="Disallow default IDs",
        description="Reject default run context identifiers.",
    )

    time_zone: TimeZone = "UTC"

    language: Language = "en"

    currency: CurrencyCode = "USD"


settings_manager = SettingsManager(RunContextSettings)
