from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class RTDBSettings(BaseSettings):
    """Settings for Firebase Realtime Database streaming."""

    model_config = SettingsConfigDict(
        env_prefix="KIARINA_LIB_FIREBASE_RTDB_",
        extra="ignore",
    )

    max_retry_delay: float = Field(
        default=60.0,
        title="Maximum retry delay",
        description="Maximum delay between retries in seconds.",
    )
    initial_retry_delay: float = Field(
        default=1.0,
        title="Initial retry delay",
        description="Initial delay between retries in seconds.",
    )
    retry_delay_multiplier: float = Field(
        default=2.0,
        title="Retry delay multiplier",
        description="Multiplier applied to the retry delay after a network error.",
    )


settings_manager = SettingsManager(RTDBSettings)
