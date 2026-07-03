from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsKey, SettingsManager

from kiarina.agi.chat_provider import ChatCapabilities
from kiarina.agi.file_info import FileType

from ._types.cache_ttl import CacheTTL


class LCAnthropicChatProviderSettings(ChatCapabilities, BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_CHAT_PROVIDER_IMPL_LC_ANTHROPIC_",
        extra="ignore",
    )

    anthropic_settings_key: SettingsKey | None = None

    model_name: str = "claude-haiku-4-5"

    token_count_model_name: str | None = None

    context_window: int = 200_000

    max_output_tokens: int = 64_000

    token_count_limit: int = 136_000

    image_file_count_limit: int = 100

    pdf_page_count_limit: int = 100

    input_enabled: dict[FileType, bool] = {
        "image": True,
        "pdf": True,
    }

    output_enabled: dict[FileType, bool] = {
        "image": True,
    }

    input_cost_microdollars_per_1k_tokens: int = 3_000

    cache_write_5m_cost_microdollars_per_1k_tokens: int = 3_750

    cache_write_1h_cost_microdollars_per_1k_tokens: int = 6_000

    cached_input_cost_microdollars_per_1k_tokens: int = 300

    output_cost_microdollars_per_1k_tokens: int = 15_000

    temperature: float = 0.0

    parallel_tool_calls: bool | None = False

    timeout: float | None = 3_600.0

    max_retry_count: int = 10

    cache_ttl: CacheTTL = "5m"

    context_1m_enabled: bool = False

    context_1m_input_cost_multiplier: float = 2.0

    context_1m_output_cost_multiplier: float = 1.5

    context_1m_threshold_tokens: int = 200_000


settings_manager = SettingsManager(LCAnthropicChatProviderSettings)
