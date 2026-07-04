from kiarina.agi.content import Content
from kiarina.agi.file_info import TextFileInfo


def test_xml_attributes() -> None:
    content = Content(description="Test description")
    assert content.xml_attributes == {"description": "Test description"}


def test_to_estimates(text_file_info: TextFileInfo) -> None:
    content = Content(text="Hello", files=[text_file_info])
    estimates = content.to_estimates()
    assert estimates.token_count == 1 + text_file_info.to_estimates().token_count


def test_to_xml(text_file_info: TextFileInfo) -> None:
    content = Content(
        text="Hello",
        files=[text_file_info],
        description="Test description",
        file_tags={text_file_info.type: "text_file"},
    )

    print(content.to_xml())
