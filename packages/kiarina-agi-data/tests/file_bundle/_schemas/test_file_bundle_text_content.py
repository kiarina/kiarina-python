import pytest
from pydantic import ValidationError

from kiarina.agi.data.file_bundle import FileBundleTextContent


def test_model_dump() -> None:
    content = FileBundleTextContent(
        text="<transcript>hello</transcript>",
        visibility="unsupported",
    )

    assert content.model_dump() == {
        "type": "text",
        "text": "<transcript>hello</transcript>",
        "visibility": "unsupported",
    }


def test_model_validate() -> None:
    content = FileBundleTextContent.model_validate(
        {
            "type": "text",
            "text": "hello",
            "visibility": "always",
        }
    )

    assert content.type == "text"
    assert content.text == "hello"
    assert content.visibility == "always"


def test_default_visibility_is_always() -> None:
    content = FileBundleTextContent.model_validate(
        {
            "type": "text",
            "text": "hi",
        }
    )

    assert content.visibility == "always"


def test_rejects_non_text_type() -> None:
    with pytest.raises(ValidationError):
        FileBundleTextContent.model_validate(
            {
                "type": "audio",
                "text": "hi",
            }
        )


def test_default_type_is_text() -> None:
    content = FileBundleTextContent(text="hi")
    assert content.type == "text"


def test_roundtrip() -> None:
    original = FileBundleTextContent(text="hello world", visibility="supported")
    restored = FileBundleTextContent.model_validate(original.model_dump())
    assert restored == original
