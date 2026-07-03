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

    organization_id: IDStr | None = None

    user_id: IDStr | None = None

    agent_id: IDStr | None = None

    node_id: IDStr | None = None

    time_zone: TimeZone = "UTC"

    language: Language = "en"

    currency: CurrencyCode = "USD"

    def get_organization_id(self) -> IDStr:
        if not self.organization_id:
            raise ValueError("organization_id is not set")

        return self.organization_id

    def get_user_id(self) -> IDStr:
        if not self.user_id:
            raise ValueError("user_id is not set")

        return self.user_id

    def get_agent_id(self) -> IDStr:
        if not self.agent_id:
            raise ValueError("agent_id is not set")

        return self.agent_id

    def get_node_id(self) -> IDStr:
        if not self.node_id:
            raise ValueError("node_id is not set")

        return self.node_id


settings_manager = SettingsManager(RunContextSettings)
