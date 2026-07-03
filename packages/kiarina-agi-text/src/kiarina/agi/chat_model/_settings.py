from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from ._schemas.chat_model_config import ChatModelConfig
from ._types.chat_model_alias import ChatModelAlias
from ._types.chat_model_name import ChatModelName
from ._types.chat_model_specifier import ChatModelSpecifier


class ChatModelSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_CHAT_MODEL_",
        extra="ignore",
    )

    default: ChatModelSpecifier = "openai"

    aliases: dict[ChatModelAlias, ChatModelName] = Field(
        default_factory=lambda: {
            # modalities
            "llm": "gpt-5.4",
            "vlm": "gpt-5.4",
            "omni": "gemini-3.1-pro-customtools",
            # providers
            "local": "qwen3.6-fast",
            "openai": "gpt-5.4",
            "anthropic": "claude-sonnet-4-6",
            "google": "gemini-3.1-pro-customtools",
        }
    )

    presets: dict[ChatModelName, ChatModelConfig] = Field(
        default_factory=lambda: {
            # --------------------------------------------------
            # mock
            # --------------------------------------------------
            "mock": ChatModelConfig(
                provider_name="mock",
                provider_config={
                    "token_count_limit": 100_000,
                    "input_enabled": {
                        "image": True,
                        "audio": True,
                        "video": True,
                        "pdf": True,
                    },
                },
                visible=False,
            ),
            # --------------------------------------------------
            # local
            # --------------------------------------------------
            "qwen3.6": ChatModelConfig(
                provider_name="lc_openai",
                provider_config={
                    "openai_settings_key": "local",
                    "model_name": "qwen3.6-27b",
                    "context_window": 262_144,
                    "max_output_tokens": 62_144,
                    "extra_body": {"chat_template_kwargs": {"enable_thinking": True}},
                    "token_count_limit": 200_000,
                    "image_file_count_limit": 100,
                    "input_enabled": {"image": True},
                },
                visible=False,
            ),
            "qwen3.6-fast": ChatModelConfig(
                provider_name="lc_openai",
                provider_config={
                    "openai_settings_key": "local",
                    "model_name": "qwen3.6-27b",
                    "context_window": 262_144,
                    "max_output_tokens": 62_144,
                    "extra_body": {"chat_template_kwargs": {"enable_thinking": False}},
                    "token_count_limit": 200_000,
                    "image_file_count_limit": 100,
                    "input_enabled": {"image": True},
                },
                visible=False,
            ),
            "qwen3-omni": ChatModelConfig(
                provider_name="lc_openai",
                provider_config={
                    "openai_settings_key": "local",
                    "model_name": "qwen3-omni",
                    "context_window": 32_000,
                    "max_output_tokens": 8_000,
                    "token_count_limit": 24_000,
                    "image_file_count_limit": 100,
                    "input_enabled": {
                        "image": True,
                        "audio": True,
                        "video": True,
                    },
                },
                visible=False,
            ),
            # -------------------------------------------------
            # lc_openai
            # --------------------------------------------------
            "gpt-5.4-nano": ChatModelConfig(
                provider_name="lc_openai",
                provider_config={
                    "model_name": "gpt-5.4-nano",
                    "context_window": 400_000,
                    "max_output_tokens": 128_000,
                    "input_cost_microdollars_per_1k_tokens": 200,
                    "cached_input_cost_microdollars_per_1k_tokens": 20,
                    "output_cost_microdollars_per_1k_tokens": 1_250,
                    "endpoint_type": "responses",
                    "token_count_limit": 272_000,
                    "image_file_count_limit": 100,
                    "pdf_page_count_limit": 100,
                    "input_enabled": {"image": True, "pdf": True},
                },
            ),
            "gpt-5.4-mini": ChatModelConfig(
                provider_name="lc_openai",
                provider_config={
                    "model_name": "gpt-5.4-mini",
                    "context_window": 400_000,
                    "max_output_tokens": 128_000,
                    "input_cost_microdollars_per_1k_tokens": 750,
                    "cached_input_cost_microdollars_per_1k_tokens": 75,
                    "output_cost_microdollars_per_1k_tokens": 4_500,
                    "endpoint_type": "responses",
                    "token_count_limit": 272_000,
                    "image_file_count_limit": 100,
                    "pdf_page_count_limit": 100,
                    "input_enabled": {"image": True, "pdf": True},
                },
            ),
            "gpt-5.4": ChatModelConfig(
                provider_name="lc_openai",
                provider_config={
                    "model_name": "gpt-5.4",
                    "context_window": 1_000_000,
                    "max_output_tokens": 128_000,
                    "input_cost_microdollars_per_1k_tokens": 2_500,
                    "cached_input_cost_microdollars_per_1k_tokens": 250,
                    "output_cost_microdollars_per_1k_tokens": 15_000,
                    "endpoint_type": "responses",
                    "token_count_limit": 772_000,
                    "image_file_count_limit": 100,
                    "pdf_page_count_limit": 100,
                    "input_enabled": {"image": True, "pdf": True},
                },
            ),
            "gpt-5.3-codex": ChatModelConfig(
                provider_name="lc_openai",
                provider_config={
                    "model_name": "gpt-5.2",
                    "context_window": 400_000,
                    "max_output_tokens": 128_000,
                    "input_cost_microdollars_per_1k_tokens": 1_750,
                    "cached_input_cost_microdollars_per_1k_tokens": 175,
                    "output_cost_microdollars_per_1k_tokens": 14_000,
                    "endpoint_type": "responses",
                    "token_count_limit": 272_000,
                    "image_file_count_limit": 100,
                    "pdf_page_count_limit": 100,
                    "input_enabled": {"image": True, "pdf": True},
                },
                visible=False,
            ),
            "gpt-5-mini": ChatModelConfig(
                provider_name="lc_openai",
                provider_config={
                    "model_name": "gpt-5-mini",
                    "context_window": 400_000,
                    "max_output_tokens": 128_000,
                    "input_cost_microdollars_per_1k_tokens": 250,
                    "cached_input_cost_microdollars_per_1k_tokens": 25,
                    "output_cost_microdollars_per_1k_tokens": 2_000,
                    "reasoning_effort": "minimal",
                    "verbosity": "medium",
                    "token_count_limit": 272_000,
                    "image_file_count_limit": 100,
                    "pdf_page_count_limit": 100,
                    "input_enabled": {"image": True, "pdf": True},
                },
            ),
            "gpt-5-nano": ChatModelConfig(
                provider_name="lc_openai",
                provider_config={
                    "model_name": "gpt-5-nano",
                    "context_window": 400_000,
                    "max_output_tokens": 128_000,
                    "input_cost_microdollars_per_1k_tokens": 50,
                    "cached_input_cost_microdollars_per_1k_tokens": 5,
                    "output_cost_microdollars_per_1k_tokens": 400,
                    "reasoning_effort": "minimal",
                    "verbosity": "medium",
                    "token_count_limit": 272_000,
                    "image_file_count_limit": 100,
                    "pdf_page_count_limit": 100,
                    "input_enabled": {"image": True, "pdf": True},
                },
                visible=False,
            ),
            "gpt-4.1": ChatModelConfig(
                provider_name="lc_openai",
                provider_config={
                    "model_name": "gpt-4.1",
                    "context_window": 1_047_576,
                    "max_output_tokens": 32_768,
                    "input_cost_microdollars_per_1k_tokens": 2_000,
                    "cached_input_cost_microdollars_per_1k_tokens": 500,
                    "output_cost_microdollars_per_1k_tokens": 8_000,
                    "token_count_limit": 1_014_808,
                    "image_file_count_limit": 100,
                    "pdf_page_count_limit": 100,
                    "input_enabled": {"image": True, "pdf": True},
                },
                visible=False,
            ),
            # --------------------------------------------------
            # lc_anthropic
            # --------------------------------------------------
            "claude-sonnet-4-6": ChatModelConfig(
                provider_name="lc_anthropic",
                provider_config={
                    "model_name": "claude-sonnet-4-6",
                    # "context_window": 200_000,
                    "context_window": 1_000_000,
                    # "max_output_tokens": 20_000,
                    "max_output_tokens": 64_000,
                    "input_cost_microdollars_per_1k_tokens": 3_000,
                    "cache_write_5m_cost_microdollars_per_1k_tokens": 3_750,
                    "cache_write_1h_cost_microdollars_per_1k_tokens": 6_000,
                    "cached_input_cost_microdollars_per_1k_tokens": 300,
                    "output_cost_microdollars_per_1k_tokens": 15_000,
                    "context_1m_enabled": True,
                    "token_count_limit": 936_000,
                    "image_file_count_limit": 100,
                    "pdf_page_count_limit": 100,
                    "input_enabled": {"image": True, "pdf": True},
                    "output_enabled": {"image": True},
                },
                token_scale_factor=0.7,
            ),
            "claude-opus-4-6": ChatModelConfig(
                provider_name="lc_anthropic",
                provider_config={
                    "model_name": "claude-opus-4-6",
                    # "context_window": 200_000,
                    "context_window": 1_000_000,
                    "max_output_tokens": 20_000,  # max 128k
                    "input_cost_microdollars_per_1k_tokens": 5_000,
                    "cache_write_5m_cost_microdollars_per_1k_tokens": 6_250,
                    "cache_write_1h_cost_microdollars_per_1k_tokens": 10_000,
                    "cached_input_cost_microdollars_per_1k_tokens": 500,
                    "output_cost_microdollars_per_1k_tokens": 25_000,
                    "context_1m_enabled": True,
                    "token_count_limit": 936_000,
                    "image_file_count_limit": 100,
                    "pdf_page_count_limit": 100,
                    "input_enabled": {"image": True, "pdf": True},
                    "output_enabled": {"image": True},
                },
                token_scale_factor=0.7,
            ),
            "claude-haiku-4-5": ChatModelConfig(
                provider_name="lc_anthropic",
                provider_config={
                    "model_name": "claude-haiku-4-5-20251001",
                    "context_window": 200_000,
                    "max_output_tokens": 20_000,  # 64k
                    "input_cost_microdollars_per_1k_tokens": 1_000,
                    "cache_write_5m_cost_microdollars_per_1k_tokens": 1_250,
                    "cache_write_1h_cost_microdollars_per_1k_tokens": 2_000,
                    "cached_input_cost_microdollars_per_1k_tokens": 100,
                    "output_cost_microdollars_per_1k_tokens": 5_000,
                    "token_count_limit": 120_000,
                    "image_file_count_limit": 100,
                    "pdf_page_count_limit": 100,
                    "input_enabled": {"image": True, "pdf": True},
                    "output_enabled": {"image": True},
                },
                token_scale_factor=0.7,
            ),
            # --------------------------------------------------
            # lc_anthropic_vertex
            # --------------------------------------------------
            "vclaude-sonnet-4-6": ChatModelConfig(
                provider_name="lc_anthropic_vertex",
                provider_config={
                    "model_name": "claude-sonnet-4-6",
                    "token_count_model_name": "claude-sonnet-4-6",
                    # "context_window": 200_000,
                    "context_window": 1_000_000,
                    # "max_output_tokens": 20_000,  # 64k
                    "max_output_tokens": 64_000,
                    "input_cost_microdollars_per_1k_tokens": 3_000,
                    "cache_write_5m_cost_microdollars_per_1k_tokens": 3_750,
                    "cache_write_1h_cost_microdollars_per_1k_tokens": 6_000,
                    "cached_input_cost_microdollars_per_1k_tokens": 300,
                    "output_cost_microdollars_per_1k_tokens": 15_000,
                    "context_1m_enabled": True,
                    "token_count_limit": 936_000,
                    "image_file_count_limit": 100,
                    "pdf_page_count_limit": 100,
                    "input_enabled": {"image": True, "pdf": True},
                    "output_enabled": {"image": True},
                },
                token_scale_factor=0.7,
                visible=False,
            ),
            "vclaude-opus-4-6": ChatModelConfig(
                provider_name="lc_anthropic_vertex",
                provider_config={
                    "model_name": "claude-opus-4-6",
                    "token_count_model_name": "claude-opus-4-6",
                    "context_window": 200_000,
                    "max_output_tokens": 20_000,  # 64k
                    "input_cost_microdollars_per_1k_tokens": 5_000,
                    "cache_write_5m_cost_microdollars_per_1k_tokens": 6_250,
                    "cache_write_1h_cost_microdollars_per_1k_tokens": 10_000,
                    "cached_input_cost_microdollars_per_1k_tokens": 500,
                    "output_cost_microdollars_per_1k_tokens": 25_000,
                    "token_count_limit": 120_000,
                    "image_file_count_limit": 100,
                    "pdf_page_count_limit": 100,
                    "input_enabled": {"image": True, "pdf": True},
                    "output_enabled": {"image": True},
                },
                token_scale_factor=0.7,
                visible=False,
            ),
            "vclaude-haiku-4-5": ChatModelConfig(
                provider_name="lc_anthropic_vertex",
                provider_config={
                    "model_name": "claude-haiku-4-5@20251001",
                    "token_count_model_name": "claude-haiku-4-5-20251001",
                    "context_window": 200_000,
                    "max_output_tokens": 20_000,  # 64k
                    "input_cost_microdollars_per_1k_tokens": 1_000,
                    "cache_write_5m_cost_microdollars_per_1k_tokens": 1_250,
                    "cache_write_1h_cost_microdollars_per_1k_tokens": 2_000,
                    "cached_input_cost_microdollars_per_1k_tokens": 100,
                    "output_cost_microdollars_per_1k_tokens": 5_000,
                    "token_count_limit": 120_000,
                    "image_file_count_limit": 100,
                    "pdf_page_count_limit": 100,
                    "input_enabled": {"image": True, "pdf": True},
                    "output_enabled": {"image": True},
                },
                token_scale_factor=0.7,
                visible=False,
            ),
            # --------------------------------------------------
            # lc_google_genai
            # --------------------------------------------------
            "gemini-3.1-flash-lite": ChatModelConfig(
                provider_name="lc_google_genai",
                provider_config={
                    "model_name": "gemini-3.1-flash-lite-preview",
                    "context_window": 1_048_576,
                    "max_output_tokens": 65_536,
                    "input_cost_microdollars_per_1k_tokens": 250,
                    "extended_input_cost_microdollars_per_1k_tokens": 250,
                    "cached_input_cost_microdollars_per_1k_tokens": 25,
                    "extended_cached_input_cost_microdollars_per_1k_tokens": 25,
                    "output_cost_microdollars_per_1k_tokens": 1500,
                    "extended_output_cost_microdollars_per_1k_tokens": 1500,
                    "token_count_limit": 1_040_768,
                    "image_file_count_limit": 3600,
                    "pdf_page_count_limit": 1000,
                    "input_enabled": {
                        "image": True,
                        "audio": True,
                        "video": True,
                        "pdf": True,
                    },
                },
                token_scale_factor=1.0,
            ),
            "gemini-3.1-pro": ChatModelConfig(
                provider_name="lc_google_genai",
                provider_config={
                    "model_name": "gemini-3.1-pro-preview",
                    "context_window": 1_048_576,
                    "max_output_tokens": 65_536,
                    "input_cost_microdollars_per_1k_tokens": 2_000,
                    "extended_input_cost_microdollars_per_1k_tokens": 4_000,
                    "cached_input_cost_microdollars_per_1k_tokens": 200,
                    "extended_cached_input_cost_microdollars_per_1k_tokens": 400,
                    "output_cost_microdollars_per_1k_tokens": 12_000,
                    "extended_output_cost_microdollars_per_1k_tokens": 18_000,
                    "token_count_limit": 983_040,
                    "image_file_count_limit": 3600,
                    "pdf_page_count_limit": 1000,
                    "input_enabled": {
                        "image": True,
                        "audio": True,
                        "video": True,
                        "pdf": True,
                    },
                },
                token_scale_factor=1.0,
            ),
            "gemini-3.1-pro-customtools": ChatModelConfig(
                provider_name="lc_google_genai",
                provider_config={
                    "model_name": "gemini-3.1-pro-preview-customtools",
                    "context_window": 1_048_576,
                    "max_output_tokens": 65_536,
                    "input_cost_microdollars_per_1k_tokens": 2_000,
                    "extended_input_cost_microdollars_per_1k_tokens": 4_000,
                    "cached_input_cost_microdollars_per_1k_tokens": 200,
                    "extended_cached_input_cost_microdollars_per_1k_tokens": 400,
                    "output_cost_microdollars_per_1k_tokens": 12_000,
                    "extended_output_cost_microdollars_per_1k_tokens": 18_000,
                    "token_count_limit": 983_040,
                    "image_file_count_limit": 3600,
                    "pdf_page_count_limit": 1000,
                    "input_enabled": {
                        "image": True,
                        "audio": True,
                        "video": True,
                        "pdf": True,
                    },
                },
                token_scale_factor=1.0,
                visible=False,
            ),
            "gemini-3-flash": ChatModelConfig(
                provider_name="lc_google_genai",
                provider_config={
                    "model_name": "gemini-3-flash-preview",
                    "context_window": 1_048_576,
                    "max_output_tokens": 65_536,
                    "input_cost_microdollars_per_1k_tokens": 500,
                    "extended_input_cost_microdollars_per_1k_tokens": 500,
                    "cached_input_cost_microdollars_per_1k_tokens": 50,
                    "extended_cached_input_cost_microdollars_per_1k_tokens": 50,
                    "output_cost_microdollars_per_1k_tokens": 3_000,
                    "extended_output_cost_microdollars_per_1k_tokens": 3_000,
                    "token_count_limit": 983_040,
                    "image_file_count_limit": 3600,
                    "pdf_page_count_limit": 1000,
                    "input_enabled": {
                        "image": True,
                        "audio": True,
                        "video": True,
                        "pdf": True,
                    },
                },
                token_scale_factor=1.0,
            ),
        }
    )

    customs: dict[ChatModelName, ChatModelConfig] = Field(default_factory=dict)


settings_manager = SettingsManager(ChatModelSettings)
