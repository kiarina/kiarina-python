from kiarina.agi.content import Content
from kiarina.agi.file_info import TextFileInfo
from kiarina.agi.message import AIMessage, ToolCall


def test_to_estimates(text_file_info: TextFileInfo) -> None:
    message = AIMessage.create(
        "Hello",
        [text_file_info],
        tool_calls=[
            ToolCall(
                id="1",
                name="search_docs",
                args={"query": "Hello"},
            ),
        ],
    )

    estimates = message.to_estimates()
    assert estimates.token_count > 0
    print(estimates)


def test_create_uses_empty_defaults() -> None:
    message = AIMessage.create()
    content = message.contents[0]

    assert message.type == "ai"
    assert len(message.contents) == 1
    assert isinstance(content, Content)
    assert content.text == ""
    assert content.files == []
    assert message.tool_calls == []


def test_create_sets_files_and_tool_calls(text_file_info: TextFileInfo) -> None:
    message = AIMessage.create(
        "hello",
        [text_file_info],
        tool_calls=[
            ToolCall(
                id="call-1",
                name="search_docs",
                args={"query": "hello"},
            )
        ],
    )
    content = message.contents[0]

    assert isinstance(content, Content)
    assert content.text == "hello"
    assert content.files == [text_file_info]
    assert len(message.tool_calls) == 1
    assert message.tool_calls[0].id == "call-1"
    assert message.tool_calls[0].name == "search_docs"
    assert message.tool_calls[0].args == {"query": "hello"}

    print(message.to_text())
