from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsKey, SettingsManager

from kiarina.agi.chat_provider import ChatCapabilities
from kiarina.agi.file_info import FileType


class LCGoogleGenAIChatProviderSettings(ChatCapabilities, BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_CHAT_PROVIDER_IMPL_LC_GOOGLE_GENAI_",
        extra="ignore",
    )

    google_auth_settings_key: SettingsKey | None = None

    model_name: str = "gemini-3.1-pro-preview"

    context_window: int = 1_048_576

    max_output_tokens: int = 65_536

    token_count_limit: int = 983_040

    image_file_count_limit: int = 3600

    pdf_page_count_limit: int = 1000

    input_enabled: dict[FileType, bool] = {
        "image": True,
        "audio": True,
        "video": True,
        "pdf": True,
    }

    input_cost_microdollars_per_1k_tokens: int = 2_000

    extended_input_cost_microdollars_per_1k_tokens: int = 4_000

    cached_input_cost_microdollars_per_1k_tokens: int = 200

    extended_cached_input_cost_microdollars_per_1k_tokens: int = 400

    output_cost_microdollars_per_1k_tokens: int = 12_000

    extended_output_cost_microdollars_per_1k_tokens: int = 18_000

    threshold_tokens: int = 200_000

    temperature: float = 0.0

    parallel_tool_calls: bool | None = False


settings_manager = SettingsManager(LCGoogleGenAIChatProviderSettings)
