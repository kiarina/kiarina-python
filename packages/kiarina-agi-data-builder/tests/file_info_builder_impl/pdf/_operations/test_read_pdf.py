import pytest

from kiarina.agi.file_info_builder_impl.pdf._operations.read_pdf import (
    read_pdf,
)


@pytest.mark.parametrize(
    "fixture_name, include_texts, image_count",
    [
        pytest.param("pdf_file_path", ["表示確認用サンプル"], 0, id="1. simple pdf"),
        pytest.param(
            "pdf_with_images_file_path",
            ["テスト用PDFドキュメント", "技術的な詳細"],
            1,
            id="2. pdf with images",
        ),
        pytest.param(
            "many_page_pdf_file_path",
            ["テスト用PDFドキュメント", "まとめ"],
            1,
            id="3. many-page pdf",
        ),
    ],
)
async def test_read_pdf(
    request: pytest.FixtureRequest,
    fixture_name: str,
    include_texts: list[str],
    image_count: int,
) -> None:
    path = request.getfixturevalue(fixture_name)
    raw_data = path.read_bytes()
    pdf = await read_pdf(raw_data)

    for text in include_texts:
        assert text in pdf.content.text

    assert len(pdf.content.images) == image_count

    print(f"PDF: file://{path.absolute()}")
    print(f"  Text content: {pdf.content.text}")
    for i, image in enumerate(pdf.content.images):
        print(f"  Image info {i + 1}: {image}")
