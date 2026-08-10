from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.utils.common import ImportPath

from ._types.scd_provider_name import SCDProviderName


class SCDProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_SCD_PROVIDER_",
        extra="ignore",
    )

    presets: dict[SCDProviderName, ImportPath] = Field(
        default_factory=lambda: {
            "mock": "kiarina.agi.scd_provider_impl.mock:create_mock_scd_provider",
            "pyannote": "kiarina.agi.scd_provider_impl.pyannote:create_pyannote_scd_provider",
        }
    )

    customs: dict[SCDProviderName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(SCDProviderSettings)
