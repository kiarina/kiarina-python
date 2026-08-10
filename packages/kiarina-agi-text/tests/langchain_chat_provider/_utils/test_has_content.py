from kiarina.agi.langchain_chat_provider import (
    LCAIMessage,
    LCHumanMessage,
    has_content,
)


def test_exists() -> None:
    assert has_content(
        [
            LCHumanMessage(content="Hello"),
            LCAIMessage(content=["Hello"]),
            LCHumanMessage(
                content=[
                    {"type": "text", "data": "Look at this image"},
                    {"type": "image", "url": "https://example.com/image.jpg"},
                ]
            ),
        ],
        "image",
    )


def test_not_exists() -> None:
    assert not has_content(
        [LCHumanMessage(content="Hello")],
        "video",
    )
