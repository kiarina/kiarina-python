from typing import Any

from kiarina.agi.event import CustomEvent, HumanMessageEvent, dehydrate_event
from kiarina.agi.message import hydrate_messages


def test_custom() -> None:
    event = CustomEvent(payload={"foo": "bar"})
    new_event, pool = dehydrate_event(event, [])
    assert new_event is event
    assert len(pool) == 0


def test_not_dehydrated() -> None:
    event = HumanMessageEvent.create("Hello")
    new_event, pool = dehydrate_event(event, [])
    assert new_event is event
    assert len(pool) == 0


def test_dehydrated(text_file_info: Any) -> None:
    event = HumanMessageEvent.create("Hello", files=[text_file_info])
    new_event, pool = dehydrate_event(event, [])
    assert new_event.type == "human_message"
    assert new_event is not event
    assert len(pool) == 1
    assert pool[0] == text_file_info

    messages, new_pool = hydrate_messages([new_event.message], pool)
    assert len(messages) == 1
    assert messages[0] == event.message
    assert len(new_pool) == 0
