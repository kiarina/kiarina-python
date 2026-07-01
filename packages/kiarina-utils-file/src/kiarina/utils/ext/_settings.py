from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class ExtSettings(BaseSettings):
    """Settings for file extensions."""

    model_config = SettingsConfigDict(env_prefix="KIARINA_UTILS_EXT_")

    custom_extensions: dict[str, str] = Field(
        default_factory=lambda: {
            "application/yaml": ".yaml",
            "image/jpeg": ".jpg",
            "text/html": ".html",
            "text/plain": ".txt",
            "text/xml": ".xml",
        },
        title="Custom extensions",
        description="MIME types mapped to file extensions.",
    )

    multi_extensions: set[str] = Field(
        default_factory=lambda: {
            ".tar.gz",
            ".tar.bz2",
            ".tar.xz",
            ".tar.lz",
            ".tar.z",
            ".tar.lzma",
            ".tar.lzo",
            ".tar.zst",
            ".tar.gz.gpg",
            ".tar.bz2.gpg",
            ".tar.xz.gpg",
        },
        title="Multi-part extensions",
        description="Recognized multi-part file extensions.",
    )

    compression_extensions: set[str] = Field(
        default_factory=lambda: {
            ".gz",
            ".bz2",
            ".xz",
            ".lz",
            ".z",
            ".lzma",
            ".lzo",
            ".zst",
        },
        title="Compression extensions",
        description="File extensions used for compression.",
    )

    archive_extensions: set[str] = Field(
        default_factory=lambda: {".tar"},
        title="Archive extensions",
        description="File extensions used for archives.",
    )

    encryption_extensions: set[str] = Field(
        default_factory=lambda: {".gpg", ".pgp"},
        title="Encryption extensions",
        description="File extensions used for encryption.",
    )

    max_multi_extension_parts: int = Field(
        default=4,
        title="Maximum multi-part extension parts",
        description="Maximum number of parts in a detected extension.",
    )


settings_manager = SettingsManager(ExtSettings)
