from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from ._schemas.asr_model_config import ASRModelConfig
from ._types.asr_model_alias import ASRModelAlias
from ._types.asr_model_name import ASRModelName
from ._types.asr_model_specifier import ASRModelSpecifier


class ASRModelSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_ASR_MODEL_",
        extra="ignore",
    )

    default: ASRModelSpecifier = "openai"

    aliases: dict[ASRModelAlias, ASRModelName] = Field(
        default_factory=lambda: {
            "local": "whisper-cli",
            "openai": "gpt-4o-mini-transcribe",
            "google": "gemini-3-flash",
        }
    )

    presets: dict[ASRModelName, ASRModelConfig] = Field(
        default_factory=lambda: {
            # --------------------------------------------------
            # mock
            # --------------------------------------------------
            "mock": ASRModelConfig(
                provider_name="mock",
            ),
            # --------------------------------------------------
            # command
            # --------------------------------------------------
            "whisper-cli": ASRModelConfig(
                provider_name="command",
                provider_config={
                    "text_command_args": [
                        "whisper-cli",
                        "-m",
                        "ggml-medium.bin",
                        "-f",
                        "-",
                        "-l",
                        "ja",
                        "--suppress-nst",
                        "--output-txt",
                        "--output-file",
                        "{output_file_stem}",
                    ],
                    "text_command_input_mode": "stdin",
                    "text_output_file_suffix": ".txt",
                    "segments_command_args": [
                        "whisper-cli",
                        "-m",
                        "ggml-medium.bin",
                        "-f",
                        "-",
                        "-l",
                        "ja",
                        "--suppress-nst",
                        "--output-srt",
                        "--output-file",
                        "{output_file_stem}",
                    ],
                    "segments_command_input_mode": "stdin",
                    "segments_output_file_suffix": ".srt",
                },
                visible=False,
            ),
            # --------------------------------------------------
            # openai
            # --------------------------------------------------
            "gpt-4o-transcribe": ASRModelConfig(
                provider_name="openai",
                provider_config={
                    "text_model_name": "gpt-4o-transcribe",
                    "segments_model_name": "gpt-4o-transcribe-diarize",
                    "text_input_cost_microdollars_per_1k_tokens": 2_500,
                    "text_output_cost_microdollars_per_1k_tokens": 10_000,
                    "segments_input_cost_microdollars_per_1k_tokens": 2_500,
                    "segments_output_cost_microdollars_per_1k_tokens": 10_000,
                },
            ),
            "gpt-4o-mini-transcribe": ASRModelConfig(
                provider_name="openai",
                provider_config={
                    "text_model_name": "gpt-4o-mini-transcribe",
                    "segments_model_name": "gpt-4o-transcribe-diarize",
                    "text_input_cost_microdollars_per_1k_tokens": 1_250,
                    "text_output_cost_microdollars_per_1k_tokens": 5_000,
                    "segments_input_cost_microdollars_per_1k_tokens": 2_500,
                    "segments_output_cost_microdollars_per_1k_tokens": 10_000,
                },
            ),
            # --------------------------------------------------
            # google
            # --------------------------------------------------
            "gemini-3.1-pro": ASRModelConfig(
                provider_name="google",
                provider_config={
                    "model_name": "gemini-3.1-pro-preview",
                    "input_cost_microdollars_per_1k_tokens": 2_000,
                    "input_audio_cost_microdollars_per_1k_tokens": 2_000,
                    "output_cost_microdollars_per_1k_tokens": 12_000,
                },
            ),
            "gemini-3-flash": ASRModelConfig(
                provider_name="google",
                provider_config={
                    "model_name": "gemini-3-flash-preview",
                    "input_cost_microdollars_per_1k_tokens": 500,
                    "input_audio_cost_microdollars_per_1k_tokens": 1_000,
                    "output_cost_microdollars_per_1k_tokens": 3_000,
                },
            ),
        }
    )

    customs: dict[ASRModelName, ASRModelConfig] = Field(default_factory=dict)


settings_manager = SettingsManager(ASRModelSettings)
