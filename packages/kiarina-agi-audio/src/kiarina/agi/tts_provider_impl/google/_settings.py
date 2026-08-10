from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsKey, SettingsManager

from ._types.speaker_name import SpeakerName
from ._types.voice_name import VoiceName


class GoogleTTSProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_TTS_PROVIDER_IMPL_GOOGLE_",
        extra="ignore",
    )

    google_auth_settings_key: SettingsKey | None = None

    model_name: str = "gemini-2.5-flash-preview-tts"

    voice_name: VoiceName = "Kore"

    speakers: dict[SpeakerName, VoiceName] = Field(default_factory=dict)

    timeout_milliseconds: int = 120_000

    input_cost_microdollars_per_1k_tokens: int = 500

    output_cost_microdollars_per_1k_tokens: int = 10_000


settings_manager = SettingsManager(GoogleTTSProviderSettings)
