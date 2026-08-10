import pytest

import kiarina.utils.mime as km


@pytest.mark.parametrize(
    "mime_type,expected",
    [
        ("application/x-yaml", "application/yaml"),
    ],
)
def test_apply_mime_alias(mime_type: str, expected: str) -> None:
    assert km.apply_mime_alias(mime_type) == expected
