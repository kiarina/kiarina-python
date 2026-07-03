import pytest

from kiarina.agi.data.content import Content
from kiarina.agi.data.message import (
    HumanMessage,
    Message,
    dehydrate_message,
    hydrate_messages,
)


def test_get_file_infos(text_file_info) -> None:
    message = HumanMessage(
        contents=[
            Content(text="Hello1", files=[text_file_info]),
            Content(text="Hello2", files=[text_file_info]),
        ],
    )

    assert len(message.get_file_infos()) == 2


def test_to_estimates(text_file_info) -> None:
    message = HumanMessage.create("Hello", files=[text_file_info])
    estimates = message.to_estimates()
    assert estimates.token_count > 0
    print(estimates)


def test_to_text() -> None:
    message = HumanMessage.create("Hello")
    assert message.to_text() == "Hello"


def test_replace_content() -> None:
    old = Content(text="old")
    new = Content(text="new")
    message = HumanMessage(contents=[old])

    replaced = message.replace_content(old, new)

    assert replaced.contents == [new]
    assert message.contents == [old]

    with pytest.raises(ValueError):
        message.replace_content(Content(text="missing"), new)


def test_shrink_not_reducible(text_file_info) -> None:
    message = HumanMessage.create("Hello", files=[text_file_info])
    print("Original text:", message.to_text())

    pool, reduced = HumanMessage.create("Hello").shrink([], 10)
    assert len(pool) == 0
    assert reduced == 0

    print("Shrunk text:", message.to_text())


def test_shrink(text_file_info) -> None:
    message: Message = HumanMessage.create("Hello", files=[text_file_info])
    print("Original text:", message.to_text())

    message, pool = dehydrate_message(message, [])
    assert len(pool) == 1

    pool, reduced = message.shrink(pool, reduce=10, reserve=5)
    assert reduced > 0

    messages, pool = hydrate_messages([message], pool)
    assert len(messages) == 1
    assert len(pool) == 0

    message = messages[0]
    print("Shrunk text:", message.to_text())
