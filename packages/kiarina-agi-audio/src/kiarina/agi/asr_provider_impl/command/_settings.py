from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from ._types.input_mode import InputMode


class CommandASRProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_ASR_PROVIDER_IMPL_COMMAND_",
        extra="ignore",
    )

    text_command_args: list[str] = []

    text_command_input_mode: InputMode = "file"

    text_output_file_suffix: str = ".txt"

    segments_command_args: list[str] = []

    segments_command_input_mode: InputMode = "file"

    segments_output_file_suffix: str = ".srt"

    timeout: float = 120.0

    encoding: str = "utf-8"


settings_manager = SettingsManager(CommandASRProviderSettings)
