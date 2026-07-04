from kiarina.agi.langchain_chat_provider import LCAIMessage, to_ai_message


def test_str() -> None:
    ai_message = to_ai_message(LCAIMessage(content="Hello"))
    assert ai_message.to_text() == "Hello"

    print("AIMessage.to_text():", ai_message.to_text())


def test_list() -> None:
    ai_message = to_ai_message(
        LCAIMessage(
            content=[
                "Hello",
                {"type": "text", "text": "World"},
            ]
        )
    )
    assert ai_message.to_text() == "Hello\n\nWorld"

    print("AIMessage.to_text():", ai_message.to_text())


def test_payload() -> None:
    ai_message = to_ai_message(
        LCAIMessage(
            content=[
                {"type": "text", "text": "Hello"},
                {"type": "image", "url": "https://example.com/image.png"},
            ]
        )
    )
    assert ai_message.contents[0].text == "Hello"
    assert ai_message.contents[1].payload == {
        "type": "image",
        "url": "https://example.com/image.png",
    }

    print("AIMessage.to_text():", ai_message.to_text())


def test_tool_calls() -> None:
    ai_message = to_ai_message(
        LCAIMessage(
            content="Hello",
            tool_calls=[
                {"id": "1", "name": "tool1", "args": {"arg1": "value1"}},
                {"id": "2", "name": "tool2", "args": {"arg2": "value2"}},
            ],
        )
    )
    assert len(ai_message.tool_calls) == 2
    assert ai_message.tool_calls[0].id == "1"
    assert ai_message.tool_calls[0].name == "tool1"
    assert ai_message.tool_calls[0].args == {"arg1": "value1"}

    print("AIMessage.to_text():", ai_message.to_text())
