import pytest

from kiarina.agi.file_info import FileInfo
from kiarina.agi.file_info_pool import FileInfoPool
from kiarina.agi.history import History
from kiarina.agi.message import HumanMessage, Message
from kiarina.agi.run_context import RunContext
from kiarina.agi.section import SectionContext
from kiarina.agi.section_impl.history import HistorySection


def dump(title: str, messages: list[Message], pool: FileInfoPool) -> None:
    print("=" * 20 + f" {title} " + "=" * 20)
    for i, file_info in enumerate(pool):
        print(f"--- pool[{i}] {file_info.type}: {file_info.to_estimates()} ---")
        print(file_info.to_xml())
    for i, message in enumerate(messages):
        print(f"--- messages[{i}] {message.type}: {message.to_estimates()} ---")
        print(message.to_text())


@pytest.fixture
async def section(history: History, run_context: RunContext) -> HistorySection:
    section = HistorySection()
    section.ctx = SectionContext.create(history=history, run_context=run_context)
    [_ async for _ in section.prepare()]
    return section


def test_prepare(section: HistorySection) -> None:
    assert len(section.messages) == 5
    assert len(section.pool) == 1


def test_get_messages(section: HistorySection) -> None:
    messages = section.get_messages()
    assert len(messages) == 5
    dump("Get Messages", messages, section.pool)


def test_is_resizable(section: HistorySection) -> None:
    assert section.is_resizable() is True

    section.pool = []
    assert section.is_resizable() is True

    section.messages = section.messages[:1]
    assert section.is_resizable() is False


async def test_resize(section: HistorySection, text_file_info: FileInfo) -> None:
    section.reserve_per_file = 0
    section.pool.append(text_file_info)

    assert len(section.messages) == 5
    assert len(section.pool) == 2

    # resize last message
    assert section.is_resizable() is True
    [_ async for _ in section.resize(100)]
    assert len(section.messages) == 5
    assert len(section.pool) == 2
    assert section.pool[0].metadata_only is True
    dump("resize last message", section.get_messages(), section.pool)

    # shrink pool
    assert section.is_resizable() is True
    [_ async for _ in section.resize(20)]
    assert len(section.messages) == 5
    assert len(section.pool) == 1
    dump("shrink pool", section.get_messages(), section.pool)

    # resize messages (human, ai)
    section.pool.clear()
    assert section.is_resizable() is True
    [_ async for _ in section.resize(1)]
    assert len(section.messages) == 3
    assert section.messages[0].type == "human"
    dump("resize messages (human, ai)", section.get_messages(), section.pool)

    # resize messages (human, ai tool call, tool)
    assert section.is_resizable() is False
    [_ async for _ in section.resize(1)]
    assert len(section.messages) == 3
    dump(
        "not resize messages (human, ai tool call, tool)",
        section.get_messages(),
        section.pool,
    )

    # append human message
    section.messages.append(HumanMessage.create("OK"))
    dump("append human message", section.get_messages(), section.pool)

    # resize messages (ai with tool call)
    assert section.is_resizable() is True
    [_ async for _ in section.resize(1)]
    assert len(section.messages) == 1
    dump("resize messages (ai with tool call)", section.get_messages(), section.pool)
