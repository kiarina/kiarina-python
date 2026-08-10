from kiarina.agi.file_info_builder_impl.pdf import (
    PDFFileInfoBuilder,
    create_pdf_file_info_builder,
)


def test_create_pdf_file_info_builder() -> None:
    builder = create_pdf_file_info_builder(analysis_enabled=True)

    assert isinstance(builder, PDFFileInfoBuilder)
    assert builder.settings.analysis_enabled is True
