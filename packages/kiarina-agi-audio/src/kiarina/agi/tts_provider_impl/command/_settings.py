from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiarina.agi.tts_provider import OutputFormat


class CommandTTSProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_TTS_PROVIDER_IMPL_COMMAND_",
        extra="ignore",
    )

    command_args: dict[OutputFormat | Literal["*"], list[str] | list[list[str]]] = (
        Field(default_factory=dict)
    )
    """
    Mapping of output formats to command argument templates.
    Each value can be a single command argument template or a sequence of command
    argument templates to run in order.
    The command argument templates should include the following placeholders:
    - {text}: the input text to be synthesized
    - {instructions}: any additional instructions for the TTS provider (optional)
    - {output_format}: the output format (e.g. "wav", "mp3")
    - {input_file}: the path to the input text file
    - {output_file}: the path to the output audio file
    - {tmp_dir}: the path to a temporary directory that can be used for intermediate files
    If a specific output format is not provided, the "*" key will be used as a fallback.
    """

    output_extensions: dict[OutputFormat, str] = Field(default_factory=dict)
    """
    Optional mapping of output formats to file extensions.
    If not provided, the output format will be used as the extension (e.g. "wav" -> ".wav").
    This is useful for cases where the output format
    does not directly correspond to a file extension (e.g. "opus" -> ".ogg").
    """

    timeout: float = 120.0


settings_manager = SettingsManager(CommandTTSProviderSettings)
