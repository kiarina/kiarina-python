from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from ._schemas.tts_model_config import TTSModelConfig
from ._types.tts_model_alias import TTSModelAlias
from ._types.tts_model_name import TTSModelName
from ._types.tts_model_specifier import TTSModelSpecifier


class TTSModelSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_TTS_MODEL_",
        extra="ignore",
    )

    default: TTSModelSpecifier = "openai"

    aliases: dict[TTSModelAlias, TTSModelName] = Field(
        default_factory=lambda: {
            "local": "voicevox",
            "openai": "gpt-4o-mini-tts",
            "google": "gemini-2.5-flash-preview-tts",
        }
    )

    presets: dict[TTSModelName, TTSModelConfig] = Field(
        default_factory=lambda: {
            # --------------------------------------------------
            # mock
            # --------------------------------------------------
            "mock": TTSModelConfig(
                provider_name="mock",
                visible=False,
            ),
            # --------------------------------------------------
            # command
            # --------------------------------------------------
            "mac-say": TTSModelConfig(
                provider_name="command",
                provider_config={
                    "command_args": {
                        "wav": [
                            "say",
                            "-f",
                            "{input_file}",
                            "-o",
                            "{output_file}",
                            "--file-format=WAVE",
                            "--data-format=LEI16",
                        ],
                        "aac": [
                            "say",
                            "-f",
                            "{input_file}",
                            "-o",
                            "{output_file}",
                            "--data-format=aac",
                        ],
                        "*": [
                            "say",
                            "-f",
                            "{input_file}",
                            "-o",
                            "{output_file}",
                            "--file-format=WAVE",
                            "--data-format=LEI16",
                        ],
                    },
                },
                visible=False,
            ),
            # --------------------------------------------------
            # voicevox
            # --------------------------------------------------
            # boot VOICEVOX engine with:
            # docker run -d --name voicevox-engine --restart unless-stopped -p 50021:50021 voicevox/voicevox_engine:cpu-latest
            # get speaker and style ids with:
            # curl -s http://127.0.0.1:50021/speakers | jq -r '.[] as $s | $s.styles[] | "\(.id)\t\($s.name)\t\(.name)"'
            # --------------------------------------------------
            "voicevox": TTSModelConfig(
                provider_name="command",
                provider_config={
                    "command_args": {
                        "*": [
                            [
                                "curl",
                                "-s",
                                "-X",
                                "POST",
                                "http://127.0.0.1:50021/audio_query?speaker=3",
                                "--get",
                                "--data-urlencode",
                                "text={text}",
                                "-o",
                                "{tmp_dir}/audio_query.json",
                            ],
                            [
                                "sh",
                                "-c",
                                'jq \'.prePhonemeLength = 0.1 | .postPhonemeLength = 0.8\' "$1" > "$2"',
                                "sh",
                                "{tmp_dir}/audio_query.json",
                                "{tmp_dir}/audio_query_padded.json",
                            ],
                            [
                                "curl",
                                "-s",
                                "-H",
                                "Content-Type: application/json",
                                "-X",
                                "POST",
                                "-d",
                                "@{tmp_dir}/audio_query_padded.json",
                                "http://127.0.0.1:50021/synthesis?speaker=3",
                                "-o",
                                "{output_file}",
                            ],
                        ]
                    }
                },
                visible=False,
            ),
            # --------------------------------------------------
            # openai
            # --------------------------------------------------
            "gpt-4o-mini-tts": TTSModelConfig(
                provider_name="openai",
                provider_config={
                    "model_name": "gpt-4o-mini-tts",
                    "voice": "marin",
                    "input_cost_microdollars_per_1k_tokens": 600,
                    "output_cost_microdollars_per_1_minute": 15_000,
                },
            ),
            # --------------------------------------------------
            # google
            # --------------------------------------------------
            "gemini-2.5-flash-preview-tts": TTSModelConfig(
                provider_name="google",
                provider_config={
                    "model_name": "gemini-2.5-flash-preview-tts",
                    "voice_name": "Kore",
                    "input_cost_microdollars_per_1k_tokens": 500,
                    "output_cost_microdollars_per_1k_tokens": 10_000,
                },
            ),
            "gemini-2.5-pro-preview-tts": TTSModelConfig(
                provider_name="google",
                provider_config={
                    "model_name": "gemini-2.5-pro-preview-tts",
                    "voice_name": "Kore",
                    "input_cost_microdollars_per_1k_tokens": 1_000,
                    "output_cost_microdollars_per_1k_tokens": 20_000,
                },
            ),
        }
    )

    customs: dict[TTSModelName, TTSModelConfig] = Field(default_factory=dict)


settings_manager = SettingsManager(TTSModelSettings)
