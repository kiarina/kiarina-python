# mypy: ignore-errors

from collections.abc import AsyncIterator

import pytest

from kiarina.agi.chat_provider import (
    BaseChatProvider,
    ChatProviderContext,
    chat_provider_registry,
)
from kiarina.agi.message import AIMessage, AIMessageChunk, HumanMessage


class ExampleChatProvider(BaseChatProvider):
    async def _run(
        self, ctx: ChatProviderContext
    ) -> AsyncIterator[AIMessageChunk | AIMessage]:
        if ctx.messages:
            yield AIMessage.create("hello")
        else:
            raise ValueError("No messages provided")


@pytest.fixture(autouse=True)
def setup():
    chat_provider_registry.register("example", ExampleChatProvider)
    yield
    chat_provider_registry.clear()


def test_base_chat_provider() -> None:
    provider = chat_provider_registry.create("example")
    assert provider.name == "example"
    print(f"chat_provider_name: {provider.name}")
    print(f"__str__: {provider!s}")


async def test_run(run_context, cost_recorder) -> None:
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
