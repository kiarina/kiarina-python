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
            "llm": "gpt-6.1-sol",
            "vlm": "gpt-6.1-sol",
            "omni": "gemini-3.8-flash",
            # providers
            "local": "qwen3.8-flash-next-fast",
            "openai": "gpt-6.1-sol",
            "anthropic": "claude-sonnet-5-5",
            "google": "gemini-3.8-flash",
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
            # because the openai provider defaults are not zero.
            "qwen3.8-flash-next": ChatModelConfig(
                provider_name="openai",
                provider_config={
                    "openai_settings_key": "local",
                    "model_name": "qwen3.8-flash-next",
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
            "qwen3.8-flash-next-fast": ChatModelConfig(
                provider_name="openai",
                provider_config={
                    "openai_settings_key": "local",
                    "model_name": "qwen3.8-flash-next",
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
            "qwen3.8-27b": ChatModelConfig(
                provider_name="openai",
                provider_config={
                    "openai_settings_key": "local",
                    "model_name": "qwen3.8-27b",
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
                provider_name="openai",
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
            # openai
            # --------------------------------------------------
            "gpt-6-astra": ChatModelConfig(
                provider_name="openai",
                provider_config={
                    "model_name": "gpt-6-astra",
                    "context_window": 1_050_000,
                    "max_output_tokens": 128_000,
                    "input_cost_microdollars_per_1k_tokens": 10_000,
                    "cached_input_cost_microdollars_per_1k_tokens": 1_000,
                    "output_cost_microdollars_per_1k_tokens": 50_000,
                    "cache_write_cost_multiplier": 1.25,
                    "extended_cost_threshold_tokens": 272_000,
                    "extended_input_cost_multiplier": 2.0,
                    "extended_output_cost_multiplier": 1.5,
                    "endpoint_type": "responses",
                    "temperature": None,
                    "token_count_limit": 800_000,
                    "image_file_count_limit": 100,
                    "pdf_page_count_limit": 100,
                    "input_enabled": {"image": True, "pdf": True},
                },
            ),
            "gpt-6.1-sol": ChatModelConfig(
                provider_name="openai",
                provider_config={
                    "model_name": "gpt-6.1-sol",
                    "context_window": 1_050_000,
                    "max_output_tokens": 128_000,
                    "input_cost_microdollars_per_1k_tokens": 2_000,
                    "cached_input_cost_microdollars_per_1k_tokens": 100,
                    "output_cost_microdollars_per_1k_tokens": 10_000,
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
            "gpt-6-luna": ChatModelConfig(
                provider_name="openai",
                provider_config={
                    "model_name": "gpt-6-luna",
                    "context_window": 1_050_000,
                    "max_output_tokens": 128_000,
                    "input_cost_microdollars_per_1k_tokens": 100,
                    "cached_input_cost_microdollars_per_1k_tokens": 10,
                    "output_cost_microdollars_per_1k_tokens": 500,
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
            # --------------------------------------------------
            # anthropic
            # --------------------------------------------------
            "claude-sonnet-5-5": ChatModelConfig(
                provider_name="anthropic",
                provider_config={
                    "model_name": "claude-sonnet-5-5",
                    "context_window": 1_000_000,
                    "max_output_tokens": 128_000,
                    "input_cost_microdollars_per_1k_tokens": 2_000,
                    "cache_write_5m_cost_microdollars_per_1k_tokens": 2_500,
                    "cache_write_1h_cost_microdollars_per_1k_tokens": 4_000,
                    "cached_input_cost_microdollars_per_1k_tokens": 200,
                    "output_cost_microdollars_per_1k_tokens": 10_000,
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
            "claude-opus-5-5": ChatModelConfig(
                provider_name="anthropic",
                provider_config={
                    "model_name": "claude-opus-5-5",
                    "context_window": 1_000_000,
                    "max_output_tokens": 128_000,
                    "input_cost_microdollars_per_1k_tokens": 4_000,
                    "cache_write_5m_cost_microdollars_per_1k_tokens": 5_000,
                    "cache_write_1h_cost_microdollars_per_1k_tokens": 8_000,
                    "cached_input_cost_microdollars_per_1k_tokens": 200,
                    "output_cost_microdollars_per_1k_tokens": 20_000,
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
            "claude-fable-5-1": ChatModelConfig(
                provider_name="anthropic",
                provider_config={
                    "model_name": "claude-fable-5-1",
                    "context_window": 1_000_000,
                    "max_output_tokens": 128_000,
                    "input_cost_microdollars_per_1k_tokens": 10_000,
                    "cache_write_5m_cost_microdollars_per_1k_tokens": 12_500,
                    "cache_write_1h_cost_microdollars_per_1k_tokens": 20_000,
                    "cached_input_cost_microdollars_per_1k_tokens": 250,
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
                provider_name="anthropic",
                provider_config={
                    "model_name": "claude-haiku-4-5-20251001",
                    "context_window": 200_000,
                    "max_output_tokens": 64_000,
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
            # anthropic_vertex
            # --------------------------------------------------
            "vclaude-sonnet-5-5": ChatModelConfig(
                provider_name="anthropic_vertex",
                provider_config={
                    "model_name": "claude-sonnet-5-5",
                    "context_window": 1_000_000,
                    "max_output_tokens": 128_000,
                    "input_cost_microdollars_per_1k_tokens": 2_000,
                    "cache_write_5m_cost_microdollars_per_1k_tokens": 2_500,
                    "cache_write_1h_cost_microdollars_per_1k_tokens": 4_000,
                    "cached_input_cost_microdollars_per_1k_tokens": 200,
                    "output_cost_microdollars_per_1k_tokens": 10_000,
                    "temperature": None,
                    "context_1m_enabled": False,
                    "vertex_ai_location": "global",
                    "token_count_limit": 872_000,
                    "image_file_count_limit": 100,
                    "pdf_page_count_limit": 100,
                    "input_enabled": {"image": True, "pdf": True},
                    "output_enabled": {"image": True},
                },
                token_scale_factor=0.7,
                visible=False,
            ),
            "vclaude-opus-5-5": ChatModelConfig(
                provider_name="anthropic_vertex",
                provider_config={
                    "model_name": "claude-opus-5-5",
                    "context_window": 1_000_000,
                    "max_output_tokens": 128_000,
                    "input_cost_microdollars_per_1k_tokens": 4_000,
                    "cache_write_5m_cost_microdollars_per_1k_tokens": 5_000,
                    "cache_write_1h_cost_microdollars_per_1k_tokens": 8_000,
                    "cached_input_cost_microdollars_per_1k_tokens": 200,
                    "output_cost_microdollars_per_1k_tokens": 20_000,
                    "temperature": None,
                    "context_1m_enabled": False,
                    "vertex_ai_location": "global",
                    "token_count_limit": 872_000,
                    "image_file_count_limit": 100,
                    "pdf_page_count_limit": 100,
                    "input_enabled": {"image": True, "pdf": True},
                    "output_enabled": {"image": True},
                },
                token_scale_factor=0.7,
                visible=False,
            ),
            "vclaude-fable-5-1": ChatModelConfig(
                provider_name="anthropic_vertex",
                provider_config={
                    "model_name": "claude-fable-5-1",
                    "context_window": 1_000_000,
                    "max_output_tokens": 128_000,
                    "input_cost_microdollars_per_1k_tokens": 10_000,
                    "cache_write_5m_cost_microdollars_per_1k_tokens": 12_500,
                    "cache_write_1h_cost_microdollars_per_1k_tokens": 20_000,
                    "cached_input_cost_microdollars_per_1k_tokens": 250,
                    "output_cost_microdollars_per_1k_tokens": 50_000,
                    "temperature": None,
                    "context_1m_enabled": False,
                    "vertex_ai_location": "global",
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
                provider_name="anthropic_vertex",
                provider_config={
                    "model_name": "claude-haiku-4-5@20251001",
                    "context_window": 200_000,
                    "max_output_tokens": 64_000,
                    "input_cost_microdollars_per_1k_tokens": 1_000,
                    "cache_write_5m_cost_microdollars_per_1k_tokens": 1_250,
                    "cache_write_1h_cost_microdollars_per_1k_tokens": 2_000,
                    "cached_input_cost_microdollars_per_1k_tokens": 100,
                    "output_cost_microdollars_per_1k_tokens": 5_000,
                    "vertex_ai_location": "global",
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
            # codex_app_server, claude_agent_sdk
            # --------------------------------------------------
            # Run with the local Codex and Claude Code logins (subscriptions), so
            # they record no cost. Each request starts a new process.
            "codex-gpt-6.1-sol": ChatModelConfig(
                provider_name="codex_app_server",
                provider_config={
                    "model_name": "gpt-6.1-sol",
                    "reasoning_effort": "low",
                    "context_window": 272_000,
                    "token_count_limit": 240_000,
                    "image_file_count_limit": 100,
                    "input_enabled": {"image": True},
                    "output_enabled": {"image": True},
                },
                visible=False,
            ),
            "claude-code-sonnet-5-5": ChatModelConfig(
                provider_name="claude_agent_sdk",
                provider_config={
                    "model_name": "claude-sonnet-5-5",
                    "context_window": 200_000,
                    "token_count_limit": 160_000,
                    "image_file_count_limit": 100,
                    "pdf_page_count_limit": 100,
                    "input_enabled": {"image": True, "pdf": True},
                    "output_enabled": {"image": True},
                },
                token_scale_factor=0.7,
                visible=False,
            ),
            # --------------------------------------------------
            # google_genai
            # --------------------------------------------------
            "gemini-3.8-flash": ChatModelConfig(
                provider_name="google_genai",
                provider_config={
                    "model_name": "gemini-3.8-flash",
                    "context_window": 1_048_576,
                    "max_output_tokens": 65_536,
                    "input_cost_microdollars_per_1k_tokens": 1_500,
                    "extended_input_cost_microdollars_per_1k_tokens": 1_500,
                    "cached_input_cost_microdollars_per_1k_tokens": 150,
                    "extended_cached_input_cost_microdollars_per_1k_tokens": 150,
                    "output_cost_microdollars_per_1k_tokens": 7_500,
                    "extended_output_cost_microdollars_per_1k_tokens": 7_500,
                    "token_count_limit": 983_040,
                    "image_file_count_limit": 3_600,
                    "pdf_page_count_limit": 1_000,
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
                provider_name="google_genai",
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
                    "image_file_count_limit": 3_600,
                    "pdf_page_count_limit": 1_000,
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
