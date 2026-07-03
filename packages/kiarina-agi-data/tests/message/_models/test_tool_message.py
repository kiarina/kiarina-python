from typing import Any

from kiarina.agi.content import Content
from kiarina.agi.message import ToolMessage


def test_create_uses_empty_defaults() -> None:
    message = ToolMessage.create(
        tool_name="search_docs",
        tool_call_id="call-1",
    )
    content = message.contents[0]

    assert message.type == "tool"
    assert message.tool_call_id == "call-1"
    assert message.tool_name == "search_docs"
    assert len(message.contents) == 1
    assert isinstance(content, Content)
    assert content.text == ""
    assert content.files == []


def test_create_sets_text_and_files(text_file_info: Any) -> None:
    message = ToolMessage.create(
        "hello",
        [text_file_info],
        tool_name="search_docs",
        tool_call_id="call-1",
    )
    content = message.contents[0]

    assert isinstance(content, Content)
    assert content.text == "hello"
    assert content.files == [text_file_info]
