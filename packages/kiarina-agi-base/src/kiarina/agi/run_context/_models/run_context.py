from typing import Any, Self
from zoneinfo import ZoneInfo

from pydantic import BaseModel, Field

from kiarina.currency import CurrencyCode
from kiarina.i18n import Language
from kiarina.utils.app import app

from .._operations.get_id import get_id
from .._settings import settings_manager
from .._types.id_str import IDStr
from .._types.time_zone import TimeZone


class RunContext(BaseModel):
    app_author: str = Field(default_factory=lambda: app.app_author)

    app_name: str = Field(default_factory=lambda: app.app_name)

    organization_id: IDStr = Field(default_factory=lambda: get_id("organization_id"))

    user_id: IDStr = Field(default_factory=lambda: get_id("user_id"))

    agent_id: IDStr = Field(default_factory=lambda: get_id("agent_id"))

    node_id: IDStr = Field(default_factory=lambda: get_id("node_id"))

    time_zone: TimeZone = Field(
        default_factory=lambda: settings_manager.get_settings().time_zone
    )

    language: Language = Field(
        default_factory=lambda: settings_manager.get_settings().language
    )

    currency: CurrencyCode = Field(
        default_factory=lambda: settings_manager.get_settings().currency
    )

    metadata: dict[str, Any] = Field(default_factory=lambda: {})

    @property
    def zone_info(self) -> ZoneInfo:
        return ZoneInfo(self.time_zone)

    def with_metadata(self, **kwargs: Any) -> Self:
        updated_metadata = {**self.metadata, **kwargs}
        return self.model_copy(update={"metadata": updated_metadata})
