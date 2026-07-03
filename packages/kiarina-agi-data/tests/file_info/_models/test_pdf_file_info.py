from kiarina.agi.file_info import PDFFileInfo


def test_export() -> None:
    file_info = PDFFileInfo(
        uri_or_file_path="/path/to/file.pdf",
        mime_type="application/pdf",
        file_hash="dummy-hash",
        file_size=1,
        token_count=10,
        intermediate_file_path=None,
        asset_uri=None,
        page_count=5,
        start_page=1,
        end_page=3,
    )

    exported = file_info.export()
    print("exported:", exported)

    assert "start_page" not in exported
    assert exported.get("end_page") == file_info.end_page


def test_to_content_estimates(pdf_file_info: PDFFileInfo) -> None:
    estimates = pdf_file_info.to_content_estimates()
    assert estimates.token_count > 0
