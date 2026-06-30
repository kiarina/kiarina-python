import pytest

from kiarina.utils.mime._operations.detect_with_dictionary import detect_with_dictionary


@pytest.mark.parametrize(
    "file_name_hint,expected",
    [
        # Test with default settings
        (
            "test.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ),
        (
            "config.pptx",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ),
        (
            "data.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ),
        ("settings.yaml", "application/yaml"),
        ("settings.yml", "application/yaml"),
        # Test with custom MIME types specified as arguments
        ("test.hoge", "application/x-hoge"),
        # Test with extensions not in dictionary
        ("test.jpeg", None),
    ],
)
def test_detect_with_dictionary(file_name_hint, expected):
    assert (
        detect_with_dictionary(
            file_name_hint,
            custom_mime_types={
                ".hoge": "application/x-hoge",
            },
        )
        == expected
    )
