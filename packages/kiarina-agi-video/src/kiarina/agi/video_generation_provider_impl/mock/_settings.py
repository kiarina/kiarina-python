from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class MockVideoGenerationProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_VIDEO_GENERATION_PROVIDER_IMPL_MOCK_",
        extra="ignore",
    )

    result_video_file_path: str | None = None
    """Path to a mock video file to use as the generated video result"""

    delay_seconds: float = 0.1
    """Delay before video is considered complete"""


settings_manager = SettingsManager(MockVideoGenerationProviderSettings)
