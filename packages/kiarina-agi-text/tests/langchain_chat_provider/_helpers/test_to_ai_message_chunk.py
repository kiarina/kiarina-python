from kiarina.agi.langchain_chat_provider import (
    LCAIMessageChunk,
    to_ai_message_chunk,
)


def test_to_ai_message_chunk() -> None:
    ai_message_chunk = to_ai_message_chunk(LCAIMessageChunk(content="Hello"))
    assert ai_message_chunk.to_text() == "Hello"

    print("AIMessageChunk.to_text():", ai_message_chunk.to_text())
