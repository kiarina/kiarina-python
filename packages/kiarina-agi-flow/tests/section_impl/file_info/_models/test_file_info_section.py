import pytest

from kiarina.agi.file_info import FileInfo
from kiarina.agi.history import History
from kiarina.agi.message import AIMessage, HumanMessage
from kiarina.agi.run_context import RunContext
from kiarina.agi.section import SectionContext
from kiarina.agi.section_impl.file_info import FileInfoSection


def dump(title: str, file_infos: list[FileInfo]) -> None:
    print("=" * 20 + f" {title} " + "=" * 20)
    for i, file_info in enumerate(file_infos):
        print(f"--- file_infos[{i}] {file_info.type}: {file_info.to_estimates()} ---")
        print(file_info.to_xml())


@pytest.fixture
async def section(history: History, run_context: RunContext) -> FileInfoSection:
    section = FileInfoSection()
    section.ctx = SectionContext.create(history=history, run_context=run_context)
    [_ async for _ in section.prepare()]
    return section


def test_prepare(section: FileInfoSection) -> None:
    assert len(section.file_infos) == 1
    dump("Prepared File Infos", section.file_infos)


def test_get_messages(section: FileInfoSection) -> None:
    messages = section.get_messages()
    assert len(messages) == 2
    assert isinstance(messages[0], HumanMessage)
    assert isinstance(messages[1], AIMessage)
    dump("Get Messages", section.file_infos)

    for i, message in enumerate(messages):
        print(f"--- messages[{i}] {message.type}: {message.to_estimates()} ---")
        print(message.to_text())


def test_is_resizable(section: FileInfoSection) -> None:
    assert section.is_resizable() is True


async def test_resize(section: FileInfoSection) -> None:
    assert len(section.file_infos) == 1

    # shrink file infos
    assert section.is_resizable() is True
    [_ async for _ in section.resize(100)]
    assert len(section.file_infos) == 1
    assert section.file_infos[0].metadata_only is True
    dump("shrink file infos", section.file_infos)

    # remove file infos
    assert section.is_resizable() is True
    [_ async for _ in section.resize(100)]
    assert len(section.file_infos) == 0
    dump("remove file infos", section.file_infos)


def test_to_string(section: FileInfoSection) -> None:
    section.group = "g1"
    section.no_group = True
    section.no_unique_key = True
    section.ignore_unique_keys = ["u1", "u2"]
    section.in_message = True
    assert "g:g1,ng,nuk,iuk:u1,u2,im" in section._to_string()
