from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class MockImageGenerationProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_IMAGE_GENERATION_PROVIDER_IMPL_MOCK_",
        extra="ignore",
    )

    image_width: int = 1024
    """Generated image width in pixels"""

    image_height: int = 1024
    """Generated image height in pixels"""

    color: tuple[int, int, int] = (100, 150, 200)
    """Default RGB color for generated images"""

    output_format: str = "png"
    """Output image format (png, jpeg, webp)"""


settings_manager = SettingsManager(MockImageGenerationProviderSettings)
