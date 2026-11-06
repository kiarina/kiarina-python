from collections.abc import AsyncIterator, Iterator
from typing import cast

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import SecretStr

from kiarina.agi.chat_model import ChatModelConfig, chat_model_registry
from kiarina.agi.chat_provider import (
    BaseChatProvider,
    ChatProviderContext,
    ChatProviderState,
    MaxTokenError,
    SafetyError,
    TokenOverflowError,
    chat_provider_registry,
)
from kiarina.agi.chat_provider_impl.proxy import (
    ProxyChatProvider,
    ProxyChatProviderSettings,
)
from kiarina.agi.chat_proxy import (
    ChatProxyError,
    ChatProxySettings,
    create_chat_proxy_app,
)
from kiarina.agi.cost_record import CostRecord
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.file import get_file_blob
from kiarina.agi.file_info import ImageFileInfo
from kiarina.agi.message import AIMessage, AIMessageChunk, HumanMessage, Message
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool_info import ToolInfo


class EchoChatProvider(BaseChatProvider):
    """Reports what reached it on the proxy, records a cost, and keeps a state."""

    async def _run(
        self, ctx: ChatProviderContext
    ) -> AsyncIterator[AIMessageChunk | AIMessage]:
        lines: list[str] = []

        for message in ctx.messages:
            for file_info in message.get_file_infos():
                if file_info.metadata_only:
                    lines.append(f"{file_info.type}:metadata_only")
                elif file_info.asset_uri:
                    blob = await get_file_blob(
                        file_info.asset_uri, run_context=ctx.run_context
                    )
                    lines.append(
                        f"{file_info.type}:{len(blob.raw_data) if blob else 0}"
                    )

        lines.append(f"tools:{','.join(t.name for t in ctx.tool_infos or [])}")
        lines.append(f"tool_choice:{ctx.tool_choice}")

        previous = ctx.messages[-2] if len(ctx.messages) > 1 else None
        state = (
            ChatProviderState.from_message(previous, self.name) if previous else None
        )
        lines.append(f"resumed:{state.data['thread'] if state else None}")

        ctx.cost_recorder.add(CostRecord(microdollars=42, kind="chat", source="echo"))

        if ctx.streaming:
            yield AIMessageChunk.create(text="part")

        ai_message = AIMessage.create(text="\n".join(lines))
        ChatProviderState(
            name=self.name, history_hash="h", data={"thread": "t1", "empty": None}
        ).write_to(ai_message)
        yield ai_message


class RaisingChatProvider(BaseChatProvider):
    def __init__(self, error: Exception) -> None:
        super().__init__()
        self.error = error

    async def _run(
        self, ctx: ChatProviderContext
    ) -> AsyncIterator[AIMessageChunk | AIMessage]:
        ctx.cost_recorder.add(CostRecord(microdollars=7, kind="chat", source="raise"))
        raise self.error
        yield  # pragma: no cover


ERRORS: dict[str, Exception] = {
    "raise-safety": SafetyError("unsafe", category="violence", request_id="req_1"),
    "raise-max-token": MaxTokenError("too long"),
    "raise-overflow": TokenOverflowError(300, limit=200),
    "raise-other": RuntimeError("boom"),
}


@pytest.fixture(autouse=True)
def register_models() -> Iterator[None]:
    names = ["echo", *ERRORS]
    chat_provider_registry.register("echo", lambda **_: EchoChatProvider())

    for name, error in ERRORS.items():
        chat_provider_registry.register(
            name, lambda error=error, **_: RaisingChatProvider(error)
        )

    for name in names:
        chat_model_registry.register_config(name, ChatModelConfig(provider_name=name))

    yield

    for name in names:
        chat_provider_registry.unregister(name)
        chat_model_registry.unregister_config(name)
        chat_model_registry.unregister(name)


@pytest.fixture
def app() -> FastAPI:
    return create_chat_proxy_app(
        ChatProxySettings(
            token=SecretStr("secret"), allowed_models=["echo", "mock", *ERRORS]
        )
    )


def create_provider(
    app: FastAPI, model_name: str = "echo", token: str | None = "secret"
) -> ProxyChatProvider:
    provider = ProxyChatProvider(
        ProxyChatProviderSettings(
            base_url="http://proxy",
            model_name=model_name,
            token=SecretStr(token) if token else None,
        ),
        client=cast(httpx.Client, TestClient(app, base_url="http://proxy")),
        async_client=httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://proxy"
        ),
    )
    provider.name = "proxy"
    return provider


async def run(
    provider: ProxyChatProvider,
    messages: list[Message],
    *,
    run_context: RunContext,
    cost_recorder: CostRecorder,
    streaming: bool = False,
    tool_infos: list[ToolInfo] | None = None,
) -> list[AIMessageChunk | AIMessage]:
    return [
        m
        async for m in provider.run(
            messages,
            tool_infos=tool_infos,
            tool_choice="auto" if tool_infos else None,
            streaming=streaming,
            cost_recorder=cost_recorder,
            run_context=run_context,
        )
    ]


async def test_round_trip(
    app: FastAPI,
    run_context: RunContext,
    cost_recorder: CostRecorder,
    image_file_info: ImageFileInfo,
    tool_infos: list[ToolInfo],
) -> None:
    provider = create_provider(app)
    missing = image_file_info.model_copy(
        update={"uri_or_file_path": "/no/such/file.png"}
    )
    first = HumanMessage.create("hi", files=[image_file_info, missing])

    results = await run(
        provider,
        [first],
        run_context=run_context,
        cost_recorder=cost_recorder,
        streaming=True,
        tool_infos=tool_infos,
    )

    assert [m.type for m in results] == ["ai_chunk", "ai"]
    final = results[-1]
    assert isinstance(final, AIMessage)
    image_size = image_file_info.file_size
    assert final.to_text().splitlines() == [
        f"image:{image_size}",
        "image:metadata_only",
        f"tools:{','.join(t.name for t in tool_infos)}",
        "tool_choice:auto",
        "resumed:None",
    ]
    assert [r.microdollars for r in cost_recorder.records] == [42]

    state = ChatProviderState.from_message(final, "echo")
    assert state is not None
    assert state.data == {"thread": "t1", "empty": None}

    results = await run(
        provider,
        [first, final, HumanMessage.create("again")],
        run_context=run_context,
        cost_recorder=cost_recorder,
    )

    assert results[-1].to_text().splitlines()[-1] == "resumed:t1"


async def test_mock_model(
    app: FastAPI, run_context: RunContext, cost_recorder: CostRecorder
) -> None:
    provider = create_provider(app, "mock")

    results = await run(
        provider,
        [HumanMessage.create("hello")],
        run_context=run_context,
        cost_recorder=cost_recorder,
    )

    assert results[-1].to_text() == "Response to: hello"
    assert provider.get_capabilities().can_include("human", "image")


@pytest.mark.parametrize("model_name", list(ERRORS))
async def test_errors(
    app: FastAPI,
    run_context: RunContext,
    cost_recorder: CostRecorder,
    model_name: str,
) -> None:
    provider = create_provider(app, model_name)
    expected = ERRORS[model_name]
    expected_type = (
        ChatProxyError if isinstance(expected, RuntimeError) else type(expected)
    )

    with pytest.raises(expected_type) as excinfo:
        await run(
            provider,
            [HumanMessage.create("hi")],
            run_context=run_context,
            cost_recorder=cost_recorder,
        )

    error = excinfo.value

    if isinstance(error, SafetyError):
        assert (error.category, error.request_id) == ("violence", "req_1")
    elif isinstance(error, TokenOverflowError):
        assert (error.token_count, error.limit) == (300, 200)
    elif isinstance(error, ChatProxyError):
        assert str(error) == "RuntimeError: boom"

    assert [r.microdollars for r in cost_recorder.records] == [7]


async def test_rejects(
    app: FastAPI, run_context: RunContext, cost_recorder: CostRecorder
) -> None:
    cases = [
        (create_provider(app, token="wrong"), "401"),
        (create_provider(app, "codex"), "403"),
    ]

    for provider, status in cases:
        with pytest.raises(ChatProxyError, match=status):
            await run(
                provider,
                [HumanMessage.create("hi")],
                run_context=run_context,
                cost_recorder=cost_recorder,
            )

        with pytest.raises(ChatProxyError, match=status):
            provider.get_capabilities()


def test_rejects_unknown_and_nested_proxy() -> None:
    app = create_chat_proxy_app(ChatProxySettings())
    chat_model_registry.register_config(
        "nested", ChatModelConfig(provider_name="proxy")
    )

    try:
        client = TestClient(app)
        assert client.get("/v1/chat-models/nested").status_code == 400
        assert client.get("/v1/chat-models/no-such-model").status_code == 404
    finally:
        chat_model_registry.unregister_config("nested")
