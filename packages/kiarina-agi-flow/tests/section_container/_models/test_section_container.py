import pytest

from kiarina.agi.chat_limits import ChatLimits
from kiarina.agi.file_info import FileInfo
from kiarina.agi.history import History
from kiarina.agi.run_context import RunContext
from kiarina.agi.section import SectionContext
from kiarina.agi.section_container import SectionContainer
from kiarina.agi.section_impl.file_info import FileInfoSection
from kiarina.agi.section_impl.history import HistorySection
from kiarina.agi.section_impl.static import StaticSection
from kiarina.agi.section_impl.tool import ToolSection
from kiarina.agi.tool_info import ToolInfo


def dump(title: str, container: SectionContainer) -> None:
    print("\n" + "=" * 20 + f" {title} " + "=" * 20)

    print(f"total: {container.get_estimates(ignore_cache=True)}")
    for i, section in enumerate(container.sections):
        print(f"--- sections[{i}] {type(section).__name__} ({section.weight}) ---")
        print(str(section.get_estimates(ignore_cache=True)))

    print("\nMessages:")
    for i, message in enumerate(container.get_messages()):
        print(f"--- messages[{i}] {message.type}: {message.to_estimates()} ---")
        print(message.to_text())


@pytest.fixture
async def container(
    history: History,
    text_file_info: FileInfo,
    tool_infos: list[ToolInfo],
    run_context: RunContext,
) -> SectionContainer:
    history.file_infos.append(text_file_info)
    history.tool_infos.extend(tool_infos)

    container = SectionContainer(
        SectionContext.create(
            history=history,
            chat_options={"tool_choice": "auto"},
            run_context=run_context,
        ),
        sections=[
            StaticSection(
                system_texts=["You are a helpful assistant."],
                ready_event={"type": "static_ready"},
            ),
            (FileInfoSection(in_message=False), 0.5),
            (HistorySection(), 0.5),
            ToolSection(),
        ],
    )

    [_ async for _ in container.prepare()]

    return container


def test_get_messages(container: SectionContainer) -> None:
    messages = container.get_messages()
    assert len(messages) == 8
    dump("Get Messages", container)


def test_get_tool_infos(container: SectionContainer) -> None:
    tool_infos = container.get_tool_infos()
    assert len(tool_infos) == 2


def test_get_estimates(container: SectionContainer) -> None:
    estimates = container.get_estimates()
    assert estimates.token_count > 0
    dump("Get Estimates", container)


def test_is_resizable(container: SectionContainer) -> None:
    assert container.is_resizable() is True


async def test_resize(container: SectionContainer) -> None:
    dump("Before Resize", container)

    def get_token_counts() -> list[int]:
        return [section.get_estimates().token_count for section in container.sections]

    token_counts_history = [get_token_counts()]

    limits = ChatLimits(token_count_limit=300)

    while True:
        estimates = container.get_estimates(ignore_cache=True)

        print(
            f"estimates: {estimates.token_count} tokens / {limits.token_count_limit} tokens",
        )

        if estimates.token_count > limits.token_count_limit:
            if not container.is_resizable():
                print("--- cannot resize anymore ---")
                dump("After Failed Resize", container)
                raise AssertionError

            [_ async for _ in container.resize(limits.token_count_limit)]

            dump(f"Resizing {limits.token_count_limit} tokens", container)
            token_counts_history.append(get_token_counts())
            continue

        break

    dump("After Resize", container)

    for i, token_counts in enumerate(token_counts_history):
        print(f"--- token counts after resize #{i} ---")
        for j, token_count in enumerate(token_counts):
            print(f"sections[{j}]: {token_count} tokens")


async def test_ready(container: SectionContainer) -> None:
    events = [event async for event in container.ready()]
    assert len(events) == 1
    assert events[0].type == "custom"
    assert events[0].payload == {"type": "static_ready"}
