from pathlib import Path

import pytest

from kiarina.agi.file_info_builder_impl.pdf._operations.build_intermediate_pdf import (
    build_intermediate_pdf,
)


@pytest.mark.parametrize(
    "start_page, end_page",
    [
        pytest.param(1, -1, id="1. all_page"),
        pytest.param(1, 1, id="2. first_page"),
        pytest.param(-1, -1, id="3. last_page"),
        pytest.param(2, 4, id="4. middle_page"),
    ],
)
async def test_build_intermediate_pdf(
    start_page: int, end_page: int, many_page_pdf_file_path: Path, tmp_path: Path
) -> None:
    input_file_path = many_page_pdf_file_path
    output_file_path = tmp_path / "extracted.pdf"

    extracted_data = await build_intermediate_pdf(
        input_file_path.read_bytes(), start_page=start_page, end_page=end_page
    )

    output_file_path.parent.mkdir(parents=True, exist_ok=True)
    output_file_path.write_bytes(extracted_data)

    print(f"Extracted PDF saved to: {output_file_path}")
