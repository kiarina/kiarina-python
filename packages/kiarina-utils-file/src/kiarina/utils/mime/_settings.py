from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class MIMESettings(BaseSettings):
    """Settings for MIME type detection."""

    model_config = SettingsConfigDict(env_prefix="KIARINA_UTILS_MIME_")

    custom_mime_types: dict[str, str] = Field(
        default_factory=lambda: {
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            ".ts": "application/typescript",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".yaml": "application/yaml",
            ".yml": "application/yaml",
        },
        title="Custom MIME types",
        description="File extensions mapped to MIME types.",
    )

    mime_aliases: dict[str, str] = Field(
        default_factory=lambda: {
            "application/x-yaml": "application/yaml",  # RFC 9512
        },
        title="MIME aliases",
        description="MIME types mapped to their preferred aliases.",
    )

    hash_algorithm: str = Field(
        default="sha256",
        title="Hash algorithm",
        description="Hash algorithm for content-based file names.",
    )


settings_manager = SettingsManager(MIMESettings)
