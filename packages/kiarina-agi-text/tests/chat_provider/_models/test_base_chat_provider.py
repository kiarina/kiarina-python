from collections.abc import AsyncIterator, Iterator
from pathlib import Path

import pytest

from kiarina.agi.chat_provider import (
    BaseChatProvider,
    ChatProviderContext,
    chat_provider_registry,
)
from kiarina.agi.cost_record import CostRecord
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.message import AIMessage, AIMessageChunk, HumanMessage
from kiarina.agi.request_logger import (
    BaseRequestLogger,
    RequestLogEntry,
    request_logger_registry,
)
from kiarina.agi.run_context import RunContext


class ExampleChatProvider(BaseChatProvider):
    async def _run(
        self, ctx: ChatProviderContext
    ) -> AsyncIterator[AIMessageChunk | AIMessage]:
        if ctx.messages:
            yield AIMessage.create("hello")
        else:
            raise ValueError("No messages provided")


class CostingChatProvider(BaseChatProvider):
    async def _run(
        self, ctx: ChatProviderContext
    ) -> AsyncIterator[AIMessageChunk | AIMessage]:
        ctx.add_cost_record(
            CostRecord(
                microdollars=7,
                kind="chat",
                source="costing",
                metadata={"input_tokens": 10, "cached_input_tokens": 90},
            )
        )
        if not ctx.messages:
            raise ValueError("No messages provided")
        yield AIMessage.create("hello")


class CapturingRequestLogger(BaseRequestLogger):
    def __init__(self) -> None:
        super().__init__()
        self.entries: list[RequestLogEntry] = []

    async def log_request_success(
        self, log_entry: RequestLogEntry, *, run_context: RunContext
    ) -> None:
        self.entries.append(log_entry)

    async def log_request_error(
        self, log_entry: RequestLogEntry, error: Exception, *, run_context: RunContext
    ) -> None:
        self.entries.append(log_entry)


@pytest.fixture(autouse=True)
def setup() -> Iterator[None]:
    chat_provider_registry.register("example", ExampleChatProvider)
    chat_provider_registry.register("costing", CostingChatProvider)
    yield
    chat_provider_registry.clear()


def test_base_chat_provider() -> None:
    provider = chat_provider_registry.create("example")
    assert provider.name == "example"
    print(f"chat_provider_name: {provider.name}")
    print(f"__str__: {provider!s}")


async def test_run(run_context: RunContext, cost_recorder: CostRecorder) -> None:
    provider = chat_provider_registry.create("example")

    ai_messages = [
        ai_message
        async for ai_message in provider.run(
            messages=[HumanMessage.create("hi")],
            cost_recorder=cost_recorder,
            run_context=run_context,
        )
    ]

    assert len(ai_messages) == 1

    with pytest.raises(ValueError, match="No messages provided"):
        async for _ in provider.run(
            [],
            cost_recorder=cost_recorder,
            run_context=run_context,
        ):
            pass


async def test_run_logs_the_cost_of_the_call(
    run_context: RunContext,
    cost_recorder: CostRecorder,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    logger = CapturingRequestLogger()
    monkeypatch.setattr(request_logger_registry, "resolve", lambda *a, **k: logger)

    async for _ in chat_provider_registry.create("costing").run(
        [HumanMessage.create("hi")],
        cost_recorder=cost_recorder,
        run_context=run_context,
    ):
        pass
    with pytest.raises(ValueError, match="No messages provided"):
        async for _ in chat_provider_registry.create("costing").run(
            [], cost_recorder=cost_recorder, run_context=run_context
        ):
            pass
    async for _ in chat_provider_registry.create("example").run(
        [HumanMessage.create("hi")],
        cost_recorder=cost_recorder,
        run_context=run_context,
    ):
        pass

    cost = {"microdollars": 7, "input_tokens": 10, "cached_input_tokens": 90}
    success, error, uncosted = logger.entries
    assert success.metadata["status"] == "success" and success.metadata["cost"] == cost
    assert error.metadata["status"] == "error" and error.metadata["cost"] == cost
    assert "cost" not in uncosted.metadata
    assert len(cost_recorder.records) == 2


def test_providers_record_cost_through_the_context() -> None:
    # A provider that adds to the recorder directly leaves the call's cost out of its log.
    root = Path(__file__).parents[3] / "src/kiarina/agi/chat_provider_impl"
    direct = [p for p in root.rglob("*.py") if "cost_recorder.add(" in p.read_text()]
    assert direct == []
