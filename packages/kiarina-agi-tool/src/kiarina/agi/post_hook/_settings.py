from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.utils.common import ImportPath

from ._types.post_hook_name import PostHookName


class PostHookSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_TOOL_POST_HOOK_",
        extra="ignore",
    )

    presets: dict[PostHookName, ImportPath] = Field(default_factory=dict)

    customs: dict[PostHookName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(PostHookSettings)
