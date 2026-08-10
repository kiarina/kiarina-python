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
        analysis_dpi=192,
    )

    exported = file_info.export()
    print("exported:", exported)

    assert "start_page" not in exported
    assert exported.get("end_page") == file_info.end_page
    assert exported.get("analysis_dpi") == 192


def test_rejects_non_positive_analysis_dpi() -> None:
    try:
        PDFFileInfo(
            uri_or_file_path="/path/to/file.pdf",
            mime_type="application/pdf",
            file_hash="dummy-hash",
            file_size=1,
            token_count=10,
            intermediate_file_path=None,
            asset_uri=None,
            page_count=1,
            analysis_dpi=0,
        )
    except ValueError:
        pass
    else:  # pragma: no cover
        raise AssertionError("analysis_dpi must reject zero")


def test_to_content_estimates(pdf_file_info: PDFFileInfo) -> None:
    estimates = pdf_file_info.to_content_estimates()
    assert estimates.token_count > 0
