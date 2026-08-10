from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsKey, SettingsManager

from ._types.reference_voice_file_path import ReferenceVoiceFilePath
from ._types.speaker_name import SpeakerName


class OpenAIASRProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_ASR_PROVIDER_IMPL_OPENAI_",
        extra="ignore",
    )

    openai_settings_key: SettingsKey | None = None

    text_model_name: str = "gpt-4o-transcribe"

    segments_model_name: str = "gpt-4o-transcribe-diarize"

    speakers: dict[SpeakerName, ReferenceVoiceFilePath] = Field(default_factory=dict)

    timeout: float = 120.0

    text_input_cost_microdollars_per_1k_tokens: int = 2_500

    text_output_cost_microdollars_per_1k_tokens: int = 10_000

    segments_input_cost_microdollars_per_1k_tokens: int = 2_500

    segments_output_cost_microdollars_per_1k_tokens: int = 10_000


settings_manager = SettingsManager(OpenAIASRProviderSettings)
