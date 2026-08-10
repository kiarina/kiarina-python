from kiarina.agi.event import HumanMessageEvent, dehydrate_events
from kiarina.agi.file_info import TextFileInfo


def test_not_dehydrated() -> None:
    event = HumanMessageEvent.create("Hello")
    new_events, pool = dehydrate_events([event], [])
    assert new_events == [event]
    assert len(pool) == 0


def test_dehydrated(text_file_info: TextFileInfo) -> None:
    event = HumanMessageEvent.create("Hello", files=[text_file_info])
    new_events, pool = dehydrate_events([event], [])
    assert len(new_events) == 1
    assert new_events[0] is not event
    assert len(pool) == 1
    assert pool[0] == text_file_info
