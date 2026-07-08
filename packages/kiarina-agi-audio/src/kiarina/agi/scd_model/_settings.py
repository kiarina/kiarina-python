from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from ._schemas.scd_model_config import SCDModelConfig
from ._types.scd_model_alias import SCDModelAlias
from ._types.scd_model_name import SCDModelName
from ._types.scd_model_specifier import SCDModelSpecifier


class SCDModelSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_SCD_MODEL_",
        extra="ignore",
    )

    default: SCDModelSpecifier = "local"

    aliases: dict[SCDModelAlias, SCDModelName] = Field(
        default_factory=lambda: {
            "local": "pyannote",
        }
    )

    presets: dict[SCDModelName, SCDModelConfig] = Field(
        default_factory=lambda: {
            "mock": SCDModelConfig(provider_name="mock"),
            "pyannote": SCDModelConfig(provider_name="pyannote"),
        }
    )

    customs: dict[SCDModelName, SCDModelConfig] = Field(default_factory=dict)


settings_manager = SettingsManager(SCDModelSettings)
