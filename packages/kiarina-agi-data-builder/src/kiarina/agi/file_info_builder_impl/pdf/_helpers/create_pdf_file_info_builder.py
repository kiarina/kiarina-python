from typing import Any

from .._models.pdf_file_info_builder import PDFFileInfoBuilder
from .._settings import PDFFileInfoBuilderSettings, settings_manager


def create_pdf_file_info_builder(**kwargs: Any) -> PDFFileInfoBuilder:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = PDFFileInfoBuilderSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return PDFFileInfoBuilder(settings)
