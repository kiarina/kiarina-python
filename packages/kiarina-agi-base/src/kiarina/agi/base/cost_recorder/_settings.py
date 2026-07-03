from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.utils.common import ImportPath

from ._types.cost_recorder_name import CostRecorderName
from ._types.cost_recorder_specifier import CostRecorderSpecifier


class CostRecorderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_COST_RECORDER_",
        extra="ignore",
    )

    default: CostRecorderSpecifier = "null"

    presets: dict[CostRecorderName, ImportPath] = Field(
        default_factory=lambda: {
            "local": "kiarina.agi.base.cost_recorder_impl.local:LocalCostRecorder",
            "null": "kiarina.agi.base.cost_recorder_impl.null:NullCostRecorder",
        }
    )

    customs: dict[CostRecorderName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(CostRecorderSettings)
