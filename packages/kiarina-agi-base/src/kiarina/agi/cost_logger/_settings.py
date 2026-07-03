from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.currency import CurrencyCode
from kiarina.utils.common import ImportPath

from ._types.cost_logger_name import CostLoggerName
from ._types.cost_logger_specifier import CostLoggerSpecifier


class CostLoggerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_COST_LOGGER_",
        extra="ignore",
    )

    default: CostLoggerSpecifier = "null"

    presets: dict[CostLoggerName, ImportPath] = Field(
        default_factory=lambda: {
            "console": "kiarina.agi.cost_logger_impl.console:ConsoleCostLogger",
            "null": "kiarina.agi.cost_logger_impl.null:NullCostLogger",
        }
    )

    customs: dict[CostLoggerName, ImportPath] = Field(default_factory=dict)

    currency: CurrencyCode | None = None

    exchange_rate: float | None = None

    decimal_places: int | None = None


settings_manager = SettingsManager(CostLoggerSettings)
