# mypy: ignore-errors

import json

import pytest

from kiarina.agi.chat_provider import (
    MaxTokenError,
    SafetyError,
    TokenOverflowError,
)
from kiarina.agi.chat_provider_impl.mock import (
    MockChatProvider,
    MockChatProviderSettings,
)
from kiarina.agi.message import HumanMessage
from kiarina.agi.tool_info import ToolInfo


@pytest.fixture
def provider() -> MockChatProvider:
    settings = MockChatProviderSettings()
    provider = MockChatProvider(settings)
    provider.name = "mock"
    return provider


async def test_invoke(provider, messages, cost_recorder, run_context) -> None:
    ai_messages = [
        ai_message
        async for ai_message in provider.run(
            messages[:-1],
            cost_recorder=cost_recorder,
            run_context=run_context,
        )
    ]

    assert len(ai_messages) == 1

    print(ai_messages[0].model_dump_json(indent=2))


async def test_stream(messages, provider, cost_recorder, run_context) -> None:
    ai_messages = [
        ai_message
        async for ai_message in provider.run(
            messages[:-1],
            streaming=True,
            cost_recorder=cost_recorder,
            run_context=run_context,
        )
    ]

    assert len(ai_messages) > 1
    assert ai_messages[0].type == "ai_chunk"
    assert ai_messages[-1].type == "ai"

    print(ai_messages[-1].model_dump_json(indent=2))


async def test_check_error_simulation(provider, cost_recorder, run_context) -> None:
    with pytest.raises(TokenOverflowError):
        async for _ in provider.run(
            [
                HumanMessage.create(
                    json.dumps({"type": "token_overflow_error", "token_count": 200_000})
                )
            ],
            cost_recorder=cost_recorder,
            run_context=run_context,
        ):
            pass

    with pytest.raises(SafetyError):
        async for _ in provider.run(
            [HumanMessage.create(json.dumps({"type": "safety_error"}))],
            cost_recorder=cost_recorder,
            run_context=run_context,
        ):
            pass

    with pytest.raises(MaxTokenError):
        async for _ in provider.run(
            [HumanMessage.create(json.dumps({"type": "max_token_error"}))],
            cost_recorder=cost_recorder,
            run_context=run_context,
        ):
            pass

    with pytest.raises(RuntimeError):
        async for _ in provider.run(
            [HumanMessage.create(json.dumps({"type": "unknown_error"}))],
            cost_recorder=cost_recorder,
            run_context=run_context,
        ):
            pass


async def test_tool_calls(provider, cost_recorder, run_context) -> None:
    ai_message = None
    async for generated_message in provider.run(
        [
            HumanMessage.create(
                json.dumps(
                    {
                        "content": "Call a tool",
                        "tool_calls": [
                            {"id": "1", "name": "hello"},
                            {"id": "2", "name": "wait", "args": {"wait_time": 1}},
                        ],
                    }
                )
            )
        ],
        tool_infos=[
            ToolInfo(name="hello", description="Hello tool"),
            ToolInfo(name="wait", description="Wait tool"),
        ],
        cost_recorder=cost_recorder,
        run_context=run_context,
    ):
        ai_message = generated_message

    assert len(ai_message.tool_calls) == 2

    print(ai_message.model_dump_json(indent=2))
