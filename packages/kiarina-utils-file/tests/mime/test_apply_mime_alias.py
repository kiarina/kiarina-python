import pytest

import kiarina.utils.mime as km


# fmt: off
@pytest.mark.parametrize(
    "mime_type,expected",
    [
        ("application/x-yaml", "application/yaml"),
    ]
)
# fmt: on
def test_apply_mime_alias(mime_type, expected):
    assert km.apply_mime_alias(mime_type) == expected
