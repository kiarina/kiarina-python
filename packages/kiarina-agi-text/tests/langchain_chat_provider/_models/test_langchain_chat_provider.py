from collections.abc import AsyncIterator
from typing import TypedDict

import pytest

from kiarina.agi.chat_provider import (
    ChatCapabilities,
    MaxTokenError,
    SafetyError,
    TokenOverflowError,
)
from kiarina.agi.cost_record import CostRecord
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.langchain_chat_provider import (
    LangChainChatProvider,
    LangChainChatProviderContext,
    LCAIMessage,
    LCAIMessageChunk,
)
from kiarina.agi.message import AIMessage, Message
from kiarina.agi.run_context import RunContext


class RunArgs(TypedDict):
    cost_recorder: CostRecorder
    run_context: RunContext


class MyChatProvider(LangChainChatProvider):
    def __init__(self) -> None:
        super().__init__()
        self.invoke_result: LCAIMessage = LCAIMessage(content="default response")
        self.stream_chunks: list[LCAIMessageChunk] = [
            LCAIMessageChunk(content="default response")
        ]
        self.request_error: Exception | None = None
        self.overflow_token_count: int | None = None
        self.cost_record: CostRecord | None = None
        self.safety_error: bool = False
        self.max_token_error: bool = False
        self._capabilities: ChatCapabilities = ChatCapabilities()

    async def _invoke(
        self,
        ctx: LangChainChatProviderContext,
    ) -> LCAIMessage:
        if self.request_error:
            raise self.request_error
        return self.invoke_result

    async def _stream(
        self,
        ctx: LangChainChatProviderContext,
    ) -> AsyncIterator[LCAIMessageChunk]:
        if self.request_error:
            raise self.request_error
        for chunk in self.stream_chunks:
            yield chunk

    def _extract_overflow_token_count(self, error: Exception) -> int | None:
        return self.overflow_token_count

    def _get_cost_record(self, lc_ai_message: LCAIMessage) -> CostRecord | None:
        return self.cost_record

    def _is_safety_error(self, lc_ai_message: LCAIMessage) -> bool:
        return self.safety_error

    def _is_max_token_error(self, lc_ai_message: LCAIMessage) -> bool:
        return self.max_token_error

    def get_capabilities(self) -> ChatCapabilities:
        return self._capabilities


@pytest.fixture
def provider(capabilities: ChatCapabilities) -> MyChatProvider:
    provider = MyChatProvider()
    provider.name = "my"
    provider._capabilities = capabilities
    return provider


@pytest.fixture
def args(cost_recorder: CostRecorder, run_context: RunContext) -> RunArgs:
    return {"cost_recorder": cost_recorder, "run_context": run_context}


async def test_invoke(
    provider: MyChatProvider, messages: list[Message], args: RunArgs
) -> None:
    ai_message = await _invoke(provider, messages, args)

    print(ai_message.to_text())


async def test_stream(
    provider: MyChatProvider, messages: list[Message], args: RunArgs
) -> None:
    async for ai_message in provider.run(messages, streaming=True, **args):
        if ai_message.type == "ai_chunk":
            print(ai_message.to_text(), end="", flush=True)

    print()
    print(ai_message.to_text())


async def test_request_error(
    provider: MyChatProvider, messages: list[Message], args: RunArgs
) -> None:
    provider.request_error = RuntimeError("Simulated request error")

    with pytest.raises(RuntimeError, match="Simulated request error"):
        await _invoke(provider, messages, args)


async def test_extract_overflow_token_count(
    provider: MyChatProvider, messages: list[Message], args: RunArgs
) -> None:
    provider.request_error = RuntimeError("Simulated token overflow error")
    provider.overflow_token_count = 12345

    with pytest.raises(TokenOverflowError) as exc_info:
        await _invoke(provider, messages, args)

    assert exc_info.value.token_count == 12345


async def test_safety_error(
    provider: MyChatProvider, messages: list[Message], args: RunArgs
) -> None:
    provider.safety_error = True

    with pytest.raises(SafetyError):
        await _invoke(provider, messages, args)


async def test_max_token_error(
    provider: MyChatProvider, messages: list[Message], args: RunArgs
) -> None:
    provider.max_token_error = True

    with pytest.raises(MaxTokenError):
        await _invoke(provider, messages, args)


async def _invoke(
    provider: MyChatProvider,
    messages: list[Message],
    args: RunArgs,
) -> AIMessage:
    ai_message = None

    async for generated_message in provider.run(messages, streaming=False, **args):
        ai_message = generated_message

    assert ai_message is not None
    return ai_message
