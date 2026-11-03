import importlib
from collections.abc import AsyncIterator
from typing import Any

import pytest

from kiarina.agi.chat_limits import ChatLimits
from kiarina.agi.chat_model import ChatModel
from kiarina.agi.chat_provider import TokenOverflowError
from kiarina.agi.event import Event
from kiarina.agi.file_info import FileInfo
from kiarina.agi.history import History
from kiarina.agi.message import AIMessage, HumanMessage, Message
from kiarina.agi.prompt import prompt, run_prompt
from kiarina.agi.run_context import RunContext
from kiarina.agi.section import BaseSection, SectionContext
from kiarina.agi.section_container import SectionContainer
from kiarina.agi.section_impl.file_info import FileInfoSection
from kiarina.agi.section_impl.history import HistorySection
from kiarina.agi.section_impl.static import StaticSection
from kiarina.agi.token_utils import TokenCount


@prompt
def SectionPrompt(ctx: SectionContext, *, sections: list[Any]) -> SectionContainer:
    return SectionContainer(ctx, sections=sections)


class DelayedSection(BaseSection):
    def __init__(self, *, steps: int = 2) -> None:
        super().__init__()
        self.steps = steps
        self.calls: list[int] = []
        self.text = "large " * 1000

    def get_messages(self) -> list[Message]:
        return [HumanMessage.create(self.text)]

    def is_resizable(self) -> bool:
        return len(self.calls) < self.steps

    async def _resize(self, reduce: TokenCount) -> AsyncIterator[Event]:
        self.calls.append(reduce)
        if len(self.calls) == self.steps:
            self.text = "small"
        if False:
            yield


async def test_local_resize_can_be_unchanged_without_compounding_limit(
    run_context: RunContext, chat_model: ChatModel, monkeypatch: pytest.MonkeyPatch
) -> None:
    section = DelayedSection(steps=3)
    fixed = StaticSection(system_texts=["Always retain these instructions."])
    chat_model.config.token_scale_factor = 0.7
    limits = ChatLimits(token_count_limit=1000)
    calls: list[list[Message]] = []
    module = importlib.import_module("kiarina.agi.prompt._helpers.run_prompt")

    async def chat(messages: list[Message], **kwargs: Any) -> AsyncIterator[AIMessage]:
        calls.append(messages)
        yield AIMessage.create("done")

    monkeypatch.setattr(module, "run_chat", chat)
    events = [
        e
        async for e in run_prompt(
            History(),
            chat_options={"chat_model": chat_model},
            prompt_options={
                "prompt": SectionPrompt(sections=[fixed, section]),
                "limits": limits,
            },
            run_context=run_context,
        )
    ]
    assert len(events) == len(calls) == 1
    assert len(section.calls) == 3 and len(set(section.calls)) == 1
    assert limits.token_count_limit == 1000
    assert "Always retain" in calls[0][0].contents_to_text()
    assert not section.is_resizable()


@pytest.mark.parametrize("kind", ["history", "weighted"])
async def test_file_resizing_through_public_prompt_preserves_history(
    text_file_info: FileInfo,
    run_context: RunContext,
    monkeypatch: pytest.MonkeyPatch,
    kind: str,
) -> None:
    # Supply a real typed file but use a synthetic large body rather than external services.
    from kiarina.agi.token_utils import calc_text_token

    text = "\n".join("line of evidence " * 20 for _ in range(300))
    file = text_file_info.model_copy(
        update={
            "raw_text": text,
            "line_count": 300,
            "start_line": 1,
            "end_line": 300,
            "token_count": calc_text_token(text),
        }
    )
    h = History()
    if kind == "history":
        h.add_message(HumanMessage.create("Read", files=[file]))
        sections: list[Any] = [StaticSection(system_texts=["fixed"]), HistorySection()]
    else:
        h.file_infos = [
            file.model_copy(update={"id": "a", "group": "a"}),
            file.model_copy(update={"id": "b", "group": "b"}),
        ]
        sections = [
            StaticSection(system_texts=["fixed"]),
            (FileInfoSection(group="a"), 0.2),
            (FileInfoSection(group="b"), 0.8),
        ]
    before = h.model_dump_json()
    captured: list[list[Message]] = []
    module = importlib.import_module("kiarina.agi.prompt._helpers.run_prompt")

    async def chat(messages: list[Message], **kwargs: Any) -> AsyncIterator[AIMessage]:
        captured.append(messages)
        yield AIMessage.create("done")

    monkeypatch.setattr(module, "run_chat", chat)
    [
        e
        async for e in run_prompt(
            h,
            chat_options={"chat_model": "mock"},
            prompt_options={
                "prompt": SectionPrompt(sections=sections),
                "limits": ChatLimits(token_count_limit=2000),
            },
            run_context=run_context,
        )
    ]
    assert len(captured) == 1
    assert sum(m.to_estimates().token_count for m in captured[0]) <= 2000
    assert h.model_dump_json() == before
    if kind == "weighted":
        files = [
            f for m in captured[0] for f in m.get_file_infos() if not f.metadata_only
        ]
        assert files[0].token_count < files[1].token_count


async def test_fixed_section_overflow_is_capacity_error(
    run_context: RunContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = importlib.import_module("kiarina.agi.prompt._helpers.run_prompt")

    async def forbidden(*args: Any, **kwargs: Any) -> AsyncIterator[AIMessage]:
        raise AssertionError("must not call a provider")
        yield

    monkeypatch.setattr(module, "run_chat", forbidden)
    with pytest.raises(TokenOverflowError) as error:
        [
            e
            async for e in run_prompt(
                History(),
                chat_options={"chat_model": "mock"},
                prompt_options={
                    "prompt": SectionPrompt(
                        sections=[
                            StaticSection(system_texts=["fixed " * 1000]),
                            DelayedSection(),
                        ]
                    ),
                    "limits": ChatLimits(token_count_limit=100),
                },
                run_context=run_context,
            )
        ]

    assert error.value.limit == 100


@pytest.mark.parametrize("actual_tokens", [2000, 0])
async def test_provider_overflow_corrects_ratio_without_increasing_unknown_allowance(
    actual_tokens: int,
    run_context: RunContext,
    chat_model: ChatModel,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = importlib.import_module("kiarina.agi.prompt._helpers.run_prompt")
    chat_model.config.token_scale_factor = 0.7
    section = DelayedSection(steps=2)
    section.text = "input " * 650
    budgets: list[int] = []
    original_resize = SectionContainer.resize
    count = 0

    async def resize(self: SectionContainer, limit: int) -> AsyncIterator[Event]:
        budgets.append(limit)
        async for event in original_resize(self, limit):
            yield event

    async def chat(messages: list[Message], **kwargs: Any) -> AsyncIterator[AIMessage]:
        nonlocal count
        count += 1
        if count == 1:
            raise TokenOverflowError(actual_tokens)
        yield AIMessage.create("done")

    monkeypatch.setattr(SectionContainer, "resize", resize)
    monkeypatch.setattr(module, "run_chat", chat)
    limits = ChatLimits(token_count_limit=1000)
    [
        e
        async for e in run_prompt(
            History(),
            chat_options={"chat_model": chat_model},
            prompt_options={
                "prompt": SectionPrompt(sections=[section]),
                "limits": limits,
            },
            run_context=run_context,
        )
    ]
    assert count == 2 and len(budgets) == 2 and budgets[0] == budgets[1]
    assert 0 < budgets[0] < 700
    assert limits.token_count_limit == 1000


async def test_empty_file_pool_exhausts_history_resize(
    text_file_info: FileInfo, run_context: RunContext
) -> None:
    file = text_file_info.model_copy(
        update={
            "raw_text": "",
            "token_count": 0,
            "line_count": 1,
            "start_line": 1,
            "end_line": 1,
        }
    )
    history = History()
    history.add_message(HumanMessage.create("Keep this message", files=[file]))
    before = history.model_dump_json()
    section = HistorySection()
    section.ctx = SectionContext.create(history=history, run_context=run_context)
    [e async for e in section.prepare()]
    assert section.is_resizable()
    [e async for e in section.resize(1000)]
    assert not section.is_resizable()
    assert section.get_messages()[0].get_file_infos()[0].metadata_only
    assert history.model_dump_json() == before
