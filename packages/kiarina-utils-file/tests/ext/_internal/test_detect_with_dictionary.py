import pytest

from kiarina.utils.ext._operations.detect_with_dictionary import detect_with_dictionary


@pytest.mark.parametrize(
    "mime_type,expected",
    [
        ("application/yaml", ".yaml"),
        ("image/jpeg", ".jpg"),
        ("text/nonexistent", None),
        ("application/custom", ".custom"),
    ],
)
def test_detect_with_dictionary(mime_type, expected) -> None:
    assert (
        detect_with_dictionary(
            mime_type,
            custom_extensions={"application/custom": "custom"},
        )
        == expected
    )
