from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsKey, SettingsManager

from ._types.segment_property import SegmentProperty
from ._types.segment_property_name import SegmentPropertyName
from ._types.speaker_description import SpeakerDescription
from ._types.speaker_name import SpeakerName


class GoogleASRProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_ASR_PROVIDER_IMPL_GOOGLE_",
        extra="ignore",
    )

    google_auth_settings_key: SettingsKey | None = None

    model_name: str = "gemini-3-flash-preview"

    speakers: dict[SpeakerName, SpeakerDescription] = Field(default_factory=dict)

    extra_segment_properties: dict[SegmentPropertyName, SegmentProperty] = Field(
        default_factory=dict
    )

    timeout_milliseconds: int = 120_000

    input_cost_microdollars_per_1k_tokens: int = 500

    input_audio_cost_microdollars_per_1k_tokens: int = 1_000

    output_cost_microdollars_per_1k_tokens: int = 3_000


settings_manager = SettingsManager(GoogleASRProviderSettings)
