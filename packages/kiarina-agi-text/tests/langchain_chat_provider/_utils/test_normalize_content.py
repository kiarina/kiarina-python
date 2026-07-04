from kiarina.agi.langchain_chat_provider import (
    LCHumanMessage,
    normalize_content,
)


def test_no_change() -> None:
    message = LCHumanMessage(content="Hello")
    normalized_message = normalize_content(message)
    assert normalized_message is message

    message = LCHumanMessage(content=["Hello", "World"])
    normalized_message = normalize_content(message)
    assert normalized_message is message


def test_empty() -> None:
    message = LCHumanMessage(content=[])
    normalized_message = normalize_content(message)
    assert normalized_message.content == ""


def test_single_text_item() -> None:
    message = LCHumanMessage(content=["Hello"])
    normalized_message = normalize_content(message)
    assert normalized_message.content == "Hello"

    message = LCHumanMessage(content=[{"type": "text", "text": "Hello"}])
    normalized_message = normalize_content(message)
    assert normalized_message.content == "Hello"
