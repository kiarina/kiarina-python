from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.utils.common import ImportPath

from ._types.prompt_name import PromptName
from ._types.prompt_specifier import PromptSpecifier


class PromptSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_FLOW_PROMPT_",
        extra="ignore",
    )

    default: PromptSpecifier = "vanilla"

    presets: dict[PromptName, ImportPath] = Field(
        default_factory=lambda: {
            "structured": "kiarina.agi.prompt_impl.structured:StructuredPrompt",
            "vanilla": "kiarina.agi.prompt_impl.vanilla:VanillaPrompt",
        }
    )

    customs: dict[PromptName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(PromptSettings)
