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
            "llm": "gpt-5.6-sol",
            "vlm": "gpt-5.6-sol",
            "omni": "gemini-3.6-flash",
            # providers
            "local": "qwen3.6-fast",
            "openai": "gpt-5.6-sol",
            "anthropic": "claude-sonnet-5",
            "google": "gemini-3.6-flash",
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
            # Local models incur no API charge. Costs are set explicitly
            # because the lc_openai provider defaults are not zero.
            "qwen3.6": ChatModelConfig(
                provider_name="lc_openai",
                provider_config={
                    "openai_settings_key": "local",
                    "model_name": "qwen3.6-27b",
                    "context_window": 262_144,
                    "max_output_tokens": 62_144,
                    "input_cost_microdollars_per_1k_tokens": 0,
                    "cached_input_cost_microdollars_per_1k_tokens": 0,
                    "output_cost_microdollars_per_1k_tokens": 0,
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
                    "input_cost_microdollars_per_1k_tokens": 0,
                    "cached_input_cost_microdollars_per_1k_tokens": 0,
                    "output_cost_microdollars_per_1k_tokens": 0,
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
                    "input_cost_microdollars_per_1k_tokens": 0,
                    "cached_input_cost_microdollars_per_1k_tokens": 0,
                    "output_cost_microdollars_per_1k_tokens": 0,
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
            # --------------------------------------------------
            # lc_openai
            # --------------------------------------------------
            "gpt-5.6-sol": ChatModelConfig(
                provider_name="lc_openai",
                provider_config={
                    "model_name": "gpt-5.6-sol",
                    "context_window": 1_050_000,
                    "max_output_tokens": 128_000,
                    "input_cost_microdollars_per_1k_tokens": 5_000,
                    "cached_input_cost_microdollars_per_1k_tokens": 500,
                    "output_cost_microdollars_per_1k_tokens": 30_000,
                    "cache_write_cost_multiplier": 1.25,
                    "extended_cost_threshold_tokens": 272_000,
                    "extended_input_cost_multiplier": 2.0,
                    "extended_output_cost_multiplier": 1.5,
                    "endpoint_type": "responses",
                    "token_count_limit": 800_000,
                    "image_file_count_limit": 100,
                    "pdf_page_count_limit": 100,
                    "input_enabled": {"image": True, "pdf": True},
                },
            ),
            "gpt-5.6-terra": ChatModelConfig(
                provider_name="lc_openai",
                provider_config={
                    "model_name": "gpt-5.6-terra",
                    "context_window": 1_050_000,
                    "max_output_tokens": 128_000,
                    "input_cost_microdollars_per_1k_tokens": 2_500,
                    "cached_input_cost_microdollars_per_1k_tokens": 250,
                    "output_cost_microdollars_per_1k_tokens": 15_000,
                    "cache_write_cost_multiplier": 1.25,
                    "extended_cost_threshold_tokens": 272_000,
                    "extended_input_cost_multiplier": 2.0,
                    "extended_output_cost_multiplier": 1.5,
                    "endpoint_type": "responses",
                    "token_count_limit": 800_000,
                    "image_file_count_limit": 100,
                    "pdf_page_count_limit": 100,
                    "input_enabled": {"image": True, "pdf": True},
                },
            ),
            "gpt-5.6-luna": ChatModelConfig(
                provider_name="lc_openai",
                provider_config={
                    "model_name": "gpt-5.6-luna",
                    "context_window": 1_050_000,
                    "max_output_tokens": 128_000,
                    "input_cost_microdollars_per_1k_tokens": 1_000,
                    "cached_input_cost_microdollars_per_1k_tokens": 100,
                    "output_cost_microdollars_per_1k_tokens": 6_000,
                    "cache_write_cost_multiplier": 1.25,
                    "extended_cost_threshold_tokens": 272_000,
                    "extended_input_cost_multiplier": 2.0,
                    "extended_output_cost_multiplier": 1.5,
                    "endpoint_type": "responses",
                    "token_count_limit": 800_000,
                    "image_file_count_limit": 100,
                    "pdf_page_count_limit": 100,
                    "input_enabled": {"image": True, "pdf": True},
                },
            ),
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
            # --------------------------------------------------
            # lc_anthropic
            # --------------------------------------------------
            "claude-sonnet-5": ChatModelConfig(
                provider_name="lc_anthropic",
                provider_config={
                    "model_name": "claude-sonnet-5",
                    "context_window": 1_000_000,
                    "max_output_tokens": 128_000,
                    "input_cost_microdollars_per_1k_tokens": 3_000,
                    "cache_write_5m_cost_microdollars_per_1k_tokens": 3_750,
                    "cache_write_1h_cost_microdollars_per_1k_tokens": 6_000,
                    "cached_input_cost_microdollars_per_1k_tokens": 300,
                    "output_cost_microdollars_per_1k_tokens": 15_000,
                    "temperature": None,
                    "context_1m_enabled": False,
                    "token_count_limit": 872_000,
                    "image_file_count_limit": 100,
                    "pdf_page_count_limit": 100,
                    "input_enabled": {"image": True, "pdf": True},
                    "output_enabled": {"image": True},
                },
                token_scale_factor=0.7,
            ),
            "claude-opus-5": ChatModelConfig(
                provider_name="lc_anthropic",
                provider_config={
                    "model_name": "claude-opus-5",
                    "context_window": 1_000_000,
                    "max_output_tokens": 128_000,
                    "input_cost_microdollars_per_1k_tokens": 5_000,
                    "cache_write_5m_cost_microdollars_per_1k_tokens": 6_250,
                    "cache_write_1h_cost_microdollars_per_1k_tokens": 10_000,
                    "cached_input_cost_microdollars_per_1k_tokens": 500,
                    "output_cost_microdollars_per_1k_tokens": 25_000,
                    "temperature": None,
                    "context_1m_enabled": False,
                    "token_count_limit": 872_000,
                    "image_file_count_limit": 100,
                    "pdf_page_count_limit": 100,
                    "input_enabled": {"image": True, "pdf": True},
                    "output_enabled": {"image": True},
                },
                token_scale_factor=0.7,
            ),
            "claude-fable-5": ChatModelConfig(
                provider_name="lc_anthropic",
                provider_config={
                    "model_name": "claude-fable-5",
                    "context_window": 1_000_000,
                    "max_output_tokens": 128_000,
                    "input_cost_microdollars_per_1k_tokens": 10_000,
                    "cache_write_5m_cost_microdollars_per_1k_tokens": 12_500,
                    "cache_write_1h_cost_microdollars_per_1k_tokens": 20_000,
                    "cached_input_cost_microdollars_per_1k_tokens": 1_000,
                    "output_cost_microdollars_per_1k_tokens": 50_000,
                    "temperature": None,
                    "context_1m_enabled": False,
                    "token_count_limit": 872_000,
                    "image_file_count_limit": 100,
                    "pdf_page_count_limit": 100,
                    "input_enabled": {"image": True, "pdf": True},
                    "output_enabled": {"image": True},
                },
                token_scale_factor=0.7,
                visible=False,
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
            "vclaude-sonnet-5": ChatModelConfig(
                provider_name="lc_anthropic_vertex",
                provider_config={
                    "model_name": "claude-sonnet-5",
                    "token_count_model_name": "claude-sonnet-5",
                    "context_window": 1_000_000,
                    "max_output_tokens": 128_000,
                    "input_cost_microdollars_per_1k_tokens": 3_000,
                    "cache_write_5m_cost_microdollars_per_1k_tokens": 3_750,
                    "cache_write_1h_cost_microdollars_per_1k_tokens": 6_000,
                    "cached_input_cost_microdollars_per_1k_tokens": 300,
                    "output_cost_microdollars_per_1k_tokens": 15_000,
                    "temperature": None,
                    "context_1m_enabled": False,
                    "token_count_limit": 872_000,
                    "image_file_count_limit": 100,
                    "pdf_page_count_limit": 100,
                    "input_enabled": {"image": True, "pdf": True},
                    "output_enabled": {"image": True},
                },
                token_scale_factor=0.7,
                visible=False,
            ),
            "vclaude-opus-5": ChatModelConfig(
                provider_name="lc_anthropic_vertex",
                provider_config={
                    "model_name": "claude-opus-5",
                    "token_count_model_name": "claude-opus-5",
                    "context_window": 1_000_000,
                    "max_output_tokens": 128_000,
                    "input_cost_microdollars_per_1k_tokens": 5_000,
                    "cache_write_5m_cost_microdollars_per_1k_tokens": 6_250,
                    "cache_write_1h_cost_microdollars_per_1k_tokens": 10_000,
                    "cached_input_cost_microdollars_per_1k_tokens": 500,
                    "output_cost_microdollars_per_1k_tokens": 25_000,
                    "temperature": None,
                    "context_1m_enabled": False,
                    "token_count_limit": 872_000,
                    "image_file_count_limit": 100,
                    "pdf_page_count_limit": 100,
                    "input_enabled": {"image": True, "pdf": True},
                    "output_enabled": {"image": True},
                },
                token_scale_factor=0.7,
                visible=False,
            ),
            "vclaude-fable-5": ChatModelConfig(
                provider_name="lc_anthropic_vertex",
                provider_config={
                    "model_name": "claude-fable-5",
                    "token_count_model_name": "claude-fable-5",
                    "context_window": 1_000_000,
                    "max_output_tokens": 128_000,
                    "input_cost_microdollars_per_1k_tokens": 10_000,
                    "cache_write_5m_cost_microdollars_per_1k_tokens": 12_500,
                    "cache_write_1h_cost_microdollars_per_1k_tokens": 20_000,
                    "cached_input_cost_microdollars_per_1k_tokens": 1_000,
                    "output_cost_microdollars_per_1k_tokens": 50_000,
                    "temperature": None,
                    "context_1m_enabled": False,
                    "token_count_limit": 872_000,
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
            "gemini-3.6-flash": ChatModelConfig(
                provider_name="lc_google_genai",
                provider_config={
                    "model_name": "gemini-3.6-flash",
                    "context_window": 1_048_576,
                    "max_output_tokens": 65_536,
                    "input_cost_microdollars_per_1k_tokens": 1_500,
                    "extended_input_cost_microdollars_per_1k_tokens": 1_500,
                    "cached_input_cost_microdollars_per_1k_tokens": 150,
                    "extended_cached_input_cost_microdollars_per_1k_tokens": 150,
                    "output_cost_microdollars_per_1k_tokens": 7_500,
                    "extended_output_cost_microdollars_per_1k_tokens": 7_500,
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
            "gemini-3.5-flash-lite": ChatModelConfig(
                provider_name="lc_google_genai",
                provider_config={
                    "model_name": "gemini-3.5-flash-lite",
                    "context_window": 1_048_576,
                    "max_output_tokens": 65_536,
                    "input_cost_microdollars_per_1k_tokens": 300,
                    "extended_input_cost_microdollars_per_1k_tokens": 300,
                    "cached_input_cost_microdollars_per_1k_tokens": 30,
                    "extended_cached_input_cost_microdollars_per_1k_tokens": 30,
                    "output_cost_microdollars_per_1k_tokens": 2_500,
                    "extended_output_cost_microdollars_per_1k_tokens": 2_500,
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
