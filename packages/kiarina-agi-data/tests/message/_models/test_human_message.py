from kiarina.agi.data.content import Content
from kiarina.agi.data.message import HumanMessage


def test_create_uses_empty_defaults() -> None:
    message = HumanMessage.create()
    content = message.contents[0]

    assert message.type == "human"
    assert len(message.contents) == 1
    assert isinstance(content, Content)
    assert content.text == ""
    assert content.files == []


def test_create_sets_text_and_files(text_file_info) -> None:
    message = HumanMessage.create("hello", [text_file_info])
    content = message.contents[0]

    assert isinstance(content, Content)
    assert content.text == "hello"
    assert content.files == [text_file_info]
