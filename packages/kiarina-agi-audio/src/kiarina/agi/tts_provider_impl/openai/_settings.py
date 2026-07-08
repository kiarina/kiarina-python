from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsKey, SettingsManager


class OpenAITTSProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_TTS_PROVIDER_IMPL_OPENAI_",
        extra="ignore",
    )

    openai_settings_key: SettingsKey | None = None

    model_name: str = "gpt-4o-mini-tts"

    voice: Literal["marin", "cedar"] = "marin"

    timeout: float = 120.0

    input_cost_microdollars_per_1k_tokens: int = 600

    output_cost_microdollars_per_1_minute: int = 15_000

    tiktoken_model_name: str = "gpt-4o"


settings_manager = SettingsManager(OpenAITTSProviderSettings)
