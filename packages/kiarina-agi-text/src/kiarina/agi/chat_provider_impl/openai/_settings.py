from typing import Any, Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsKey, SettingsManager

from kiarina.agi.chat_provider import ChatCapabilities, OpenAITokenPricing
from kiarina.agi.file_info import FileType


class OpenAIChatProviderSettings(ChatCapabilities, OpenAITokenPricing, BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_CHAT_PROVIDER_IMPL_OPENAI_",
        extra="ignore",
    )

    openai_settings_key: SettingsKey | None = None

    model_name: str = "gpt-6.2-sol"

    max_output_tokens: int = 128_000

    context_window: int = 1_050_000

    token_count_limit: int = 800_000

    image_file_count_limit: int = 100

    pdf_page_count_limit: int = 100

    input_enabled: dict[FileType, bool] = {
        "image": True,
        "pdf": True,
    }

    # The pricing of the default model.
    input_cost_microdollars_per_1k_tokens: int = 2_000

    cached_input_cost_microdollars_per_1k_tokens: int = 100

    output_cost_microdollars_per_1k_tokens: int = 10_000

    cache_write_cost_multiplier: float = 1.25

    extended_cost_threshold_tokens: int | None = 272_000

    extended_input_cost_multiplier: float = 2.0

    extended_output_cost_multiplier: float = 1.5

    temperature: float | None = Field(
        default=1.0,
        title="Temperature",
        description="Sampling temperature. None omits it, for models that reject it.",
    )

    parallel_tool_calls: bool | None = False

    timeout: float | None = 3_600.0

    reasoning_effort: Literal["none", "minimal", "low", "medium", "high"] | None = None

    verbosity: Literal["low", "medium", "high"] | None = None

    endpoint_type: Literal["chat_completions", "responses"] = "chat_completions"

    extra_body: dict[str, Any] | None = None

    carry_reasoning: bool = True
    """
    Responses API: ask for encrypted reasoning items and send them back with
    their turn. Turn it off for a model that rejects `reasoning.encrypted_content`.
    """


settings_manager = SettingsManager(OpenAIChatProviderSettings)
