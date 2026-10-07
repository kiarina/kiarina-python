from kiarina.agi.chat_content import ContentPart
from kiarina.agi.chat_provider_impl.openai._operations.to_openai_parts import (
    to_openai_parts,
)


def test_single_text_collapses_to_string() -> None:
    parts = [{"type": "text", "text": "Hello", "cache_control": {"type": "ephemeral"}}]
    assert to_openai_parts(parts) == "Hello"


def test_empty() -> None:
    assert to_openai_parts([]) == ""


def test_text_type_and_media() -> None:
    parts: list[ContentPart] = [
        {"type": "text", "text": "Look", "cache_control": {"type": "ephemeral"}},
        {"type": "input_image", "image_url": "data:"},
    ]

    assert to_openai_parts(parts, text_type="input_text") == [
        {"type": "input_text", "text": "Look"},
        {"type": "input_image", "image_url": "data:"},
    ]
