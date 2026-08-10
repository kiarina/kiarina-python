from typing import Any, Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsKey, SettingsManager

from kiarina.agi.chat_provider import ChatCapabilities
from kiarina.agi.file_info import FileType


class LCOpenAIChatProviderSettings(ChatCapabilities, BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_CHAT_PROVIDER_IMPL_LC_OPENAI_",
        extra="ignore",
    )

    openai_settings_key: SettingsKey | None = None

    model_name: str = "gpt-5.5"

    max_output_tokens: int = 128_000

    context_window: int = 400_000

    token_count_limit: int = 272_000

    image_file_count_limit: int = 100

    pdf_page_count_limit: int = 100

    input_enabled: dict[FileType, bool] = {
        "image": True,
        "pdf": True,
    }

    input_cost_microdollars_per_1k_tokens: int = 50

    cached_input_cost_microdollars_per_1k_tokens: int = 5

    output_cost_microdollars_per_1k_tokens: int = 400

    cache_write_cost_multiplier: float = Field(
        default=1.0,
        title="Cache Write Cost Multiplier",
        description="Multiplier applied to uncached input pricing for cache writes.",
    )

    extended_cost_threshold_tokens: int | None = Field(
        default=None,
        title="Extended Cost Threshold Tokens",
        description="Input token threshold above which extended pricing applies.",
    )

    extended_input_cost_multiplier: float = Field(
        default=1.0,
        title="Extended Input Cost Multiplier",
        description="Input cost multiplier applied above the extended cost threshold.",
    )

    extended_output_cost_multiplier: float = Field(
        default=1.0,
        title="Extended Output Cost Multiplier",
        description="Output cost multiplier applied above the extended cost threshold.",
    )

    temperature: float = 1.0

    parallel_tool_calls: bool | None = False

    timeout: float | None = 3_600.0

    tiktoken_model_name: str = "gpt-4o"

    reasoning_effort: Literal["none", "minimal", "low", "medium", "high"] | None = None

    verbosity: Literal["low", "medium", "high"] | None = None

    endpoint_type: Literal["chat_completions", "responses"] = "chat_completions"

    extra_body: dict[str, Any] | None = None


settings_manager = SettingsManager(LCOpenAIChatProviderSettings)
