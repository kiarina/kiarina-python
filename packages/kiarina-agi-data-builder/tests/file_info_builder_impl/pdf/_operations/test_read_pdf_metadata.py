import pytest

from kiarina.agi.file_info_builder_impl.pdf._operations.read_pdf_metadata import (
    read_pdf_metadata,
)


@pytest.mark.parametrize(
    "fixture_name, expected_page_count",
    [
        ("pdf_file_path", 1),
        ("many_page_pdf_file_path", 3),
    ],
)
async def test_read_pdf_metadata(
    request: pytest.FixtureRequest, fixture_name: str, expected_page_count: int
) -> None:
    path = request.getfixturevalue(fixture_name)
    raw_data = path.read_bytes()
    metadata = await read_pdf_metadata(raw_data)

    assert metadata.page_count == expected_page_count
