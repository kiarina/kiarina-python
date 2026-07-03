from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.agi.chat_provider import ChatCapabilities
from kiarina.agi.file_info import FileType


class MockChatProviderSettings(ChatCapabilities, BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_CHAT_PROVIDER_IMPL_MOCK_",
        extra="ignore",
    )

    # --------------------------------------------------
    # Delay Simulation
    # --------------------------------------------------

    simulate_delay: bool = True
    """Whether to simulate processing delay"""

    delay_seconds: float = 0.1
    """Delay in seconds for invoke operations"""

    stream_delay_seconds: float = 0.01
    """Delay in seconds between stream chunks"""

    stream_chunk_size: int = 10
    """Number of characters per stream chunk"""

    token_count_limit: int = 100_000

    input_enabled: dict[FileType, bool] = {
        "image": True,
        "audio": True,
        "video": True,
        "pdf": True,
    }

    # --------------------------------------------------
    # Feature Support
    # --------------------------------------------------

    support_image_input: bool = True
    """Whether to support image input"""

    support_audio_input: bool = True
    """Whether to support audio input"""

    support_video_input: bool = True
    """Whether to support video input"""

    support_pdf_input: bool = True
    """Whether to support PDF input"""


settings_manager = SettingsManager(MockChatProviderSettings)
