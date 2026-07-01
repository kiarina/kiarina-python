from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class EncodingSettings(BaseSettings):
    """Settings for encoding detection."""

    model_config = SettingsConfigDict(env_prefix="KIARINA_UTILS_ENCODING_")

    use_nkf: bool | None = Field(
        default=None,
        title="Use nkf",
        description="Use nkf for encoding detection. Detect automatically when unset.",
    )

    fallback_encodings: list[str] = Field(
        default_factory=lambda: ["utf-8", "shift_jis", "euc-jp", "iso2022_jp"],
        title="Fallback encodings",
        description="Encodings to try when detection fails.",
    )

    default_encoding: str = Field(
        default="utf-8",
        title="Default encoding",
        description="Encoding to use when detection fails.",
    )

    max_sample_size: int = Field(
        default=8192,
        title="Maximum sample size",
        description="Maximum number of bytes used for detection.",
    )

    charset_normalizer_confidence_threshold: float = Field(
        default=0.6,
        title="Charset Normalizer confidence threshold",
        description="Minimum confidence accepted from Charset Normalizer.",
    )


settings_manager = SettingsManager(EncodingSettings)
