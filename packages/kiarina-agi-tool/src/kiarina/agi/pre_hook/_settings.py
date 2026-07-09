from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.utils.common import ImportPath

from ._types.pre_hook_name import PreHookName


class PreHookSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_TOOL_PRE_HOOK_",
        extra="ignore",
    )

    presets: dict[PreHookName, ImportPath] = Field(
        default_factory=lambda: {
            "confirm": "kiarina.agi.pre_hook_impl.confirm:ConfirmPreHook",
        }
    )

    customs: dict[PreHookName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(PreHookSettings)
