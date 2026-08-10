from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class PDFFileInfoBuilderSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARINA_AGI_FILE_INFO_BUILDER_IMPL_PDF_",
        extra="ignore",
    )

    analysis_enabled: bool = Field(
        default=False,
        title="Analysis Enabled",
        description="Whether to build capability-aware PDF analysis bundles.",
    )


settings_manager = SettingsManager(PDFFileInfoBuilderSettings)
