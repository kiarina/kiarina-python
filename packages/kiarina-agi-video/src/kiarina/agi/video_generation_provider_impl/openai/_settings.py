from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsKey, SettingsManager

from ._types.model_name import ModelName
from ._types.seconds import Seconds
from ._types.size import Size


class OpenAIVideoGenerationProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_VIDEO_GENERATION_PROVIDER_IMPL_OPENAI_",
        extra="ignore",
    )

    openai_settings_key: SettingsKey | None = None

    model_name: ModelName = "sora-2"

    size: Size = "1280x720"

    seconds: Seconds = "4"

    timeout: float = 3600.0

    cost_microdollars_720p_per_second: int = 300_000  # $0.30/sec

    cost_microdollars_1024p_per_second: int = 500_000  # $0.50/sec


settings_manager = SettingsManager(OpenAIVideoGenerationProviderSettings)
