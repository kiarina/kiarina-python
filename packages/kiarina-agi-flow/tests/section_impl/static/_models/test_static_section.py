from kiarina.agi.event import CustomEvent
from kiarina.agi.section_impl.static import StaticSection


async def test_static_section() -> None:
    section = StaticSection()

    assert len(section.get_system_texts()) == 0
    assert len(section.get_messages()) == 0
    assert len(section.get_tool_infos()) == 0


async def test_ready() -> None:
    section = StaticSection()
    events = [e async for e in section.ready()]
    assert len(events) == 0

    section = StaticSection(ready_event={"type": "ready"})
    events = [e async for e in section.ready()]
    assert len(events) == 1

    section = StaticSection(ready_event=CustomEvent(payload={"type": "ready"}))
    events = [e async for e in section.ready()]
    assert len(events) == 1
