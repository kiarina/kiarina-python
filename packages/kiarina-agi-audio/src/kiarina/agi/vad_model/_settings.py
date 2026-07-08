from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from ._schemas.vad_model_config import VADModelConfig
from ._types.vad_model_alias import VADModelAlias
from ._types.vad_model_name import VADModelName
from ._types.vad_model_specifier import VADModelSpecifier


class VADModelSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_VAD_MODEL_",
        extra="ignore",
    )

    default: VADModelSpecifier = "local"

    aliases: dict[VADModelAlias, VADModelName] = Field(
        default_factory=lambda: {
            "local": "silero",
        }
    )

    presets: dict[VADModelName, VADModelConfig] = Field(
        default_factory=lambda: {
            "mock": VADModelConfig(provider_name="mock"),
            "silero": VADModelConfig(provider_name="silero"),
        }
    )

    customs: dict[VADModelName, VADModelConfig] = Field(default_factory=dict)


settings_manager = SettingsManager(VADModelSettings)
