from typing import Any

import pytest

from kiarina.agi.chat_provider import ChatCapabilities
from kiarina.agi.chat_provider_impl.anthropic import (
    AnthropicChatProvider,
    AnthropicChatProviderSettings,
)
from kiarina.agi.chat_provider_impl.anthropic._operations.to_anthropic_request import (
    to_anthropic_request,
)
from kiarina.agi.chat_provider_impl.anthropic._schemas.anthropic_request import (
    AnthropicRequest,
)
from kiarina.agi.content import Content
from kiarina.agi.message import (
    AIMessage,
    HumanMessage,
    Message,
    SystemMessage,
    ToolCall,
    ToolMessage,
)
from kiarina.agi.run_context import RunContext


@pytest.fixture
def convert(capabilities: ChatCapabilities, run_context: RunContext) -> Any:
    async def convert(
        messages: list[Message], model_name: str = "claude-haiku-4-5"
    ) -> AnthropicRequest:
        return await to_anthropic_request(
            messages,
            model_name=model_name,
            capabilities=capabilities,
            media_converter=AnthropicChatProvider(AnthropicChatProviderSettings()),
            run_context=run_context,
        )

    return convert


async def test_conversation(convert: Any, messages: list[Message]) -> None:
    request = await convert([SystemMessage.create("Be kind."), *messages])

    assert request.system == "Be kind."
    assert [m["role"] for m in request.messages] == [
        "user",
        "assistant",
        "user",
        "assistant",
        "user",
        "assistant",
    ]
    assert request.messages[3]["content"] == [
        {
            "type": "tool_use",
            "id": "123",
            "name": "generate_image",
            "input": {"instructions": "Create a image of a cat"},
        }
    ]

    # The tool result and the purged image share the user turn after the tool use.
    tool_turn = request.messages[4]["content"]
    assert tool_turn[0]["type"] == "tool_result"
    assert tool_turn[0]["tool_use_id"] == "123"
    assert any(block["type"] == "image" for block in tool_turn[1:])


async def test_system_with_cache_control(convert: Any) -> None:
    request = await convert(
        [
            SystemMessage(
                contents=[Content(text="Be kind.", cache_control={"type": "ephemeral"})]
            ),
            HumanMessage.create("Hello"),
        ]
    )

    assert request.system == [
        {"type": "text", "text": "Be kind.", "cache_control": {"type": "ephemeral"}}
    ]


async def test_mid_conversation_system_in_place(convert: Any) -> None:
    request = await convert(
        [
            HumanMessage.create("Hello"),
            SystemMessage.create("Reply in Japanese."),
            AIMessage.create("こんにちは"),
            HumanMessage.create("Bye"),
            SystemMessage.create("Be brief."),
        ],
        model_name="claude-opus-5",
    )

    assert request.system is None
    assert [m["role"] for m in request.messages] == [
        "user",
        "system",
        "assistant",
        "user",
        "system",
    ]


async def test_mid_conversation_system_before_user_is_hoisted(convert: Any) -> None:
    request = await convert(
        [
            HumanMessage.create("Hello"),
            SystemMessage.create("Reply in Japanese."),
            HumanMessage.create("Bye"),
        ],
        model_name="claude-opus-5",
    )

    assert request.system == "Reply in Japanese."
    assert [m["role"] for m in request.messages] == ["user"]


async def test_mid_conversation_system_hoisted_for_unsupported_model(
    convert: Any,
) -> None:
    request = await convert(
        [HumanMessage.create("Hello"), SystemMessage.create("Reply in Japanese.")]
    )

    assert request.system == "Reply in Japanese."


async def test_multiple_non_consecutive_system_messages(convert: Any) -> None:
    with pytest.raises(ValueError, match="non-consecutive system messages"):
        await convert(
            [
                SystemMessage.create("A"),
                HumanMessage.create("Hello"),
                SystemMessage.create("B"),
            ]
        )


async def test_empty_contents(convert: Any) -> None:
    request = await convert(
        [
            HumanMessage.create(""),
            AIMessage.create(""),
            HumanMessage.create("Hello"),
            AIMessage.create("Partial answer   "),
        ]
    )

    assert request.messages[0]["content"] == [{"type": "text", "text": "<no message>"}]
    assert request.messages[1]["content"] == [{"type": "text", "text": "<no message>"}]
    assert request.messages[3]["content"] == [
        {"type": "text", "text": "Partial answer"}
    ]


async def test_tool_results(convert: Any) -> None:
    request = await convert(
        [
            HumanMessage.create("Hello"),
            AIMessage.create(
                tool_calls=[ToolCall(id="a", name="f"), ToolCall(id="b", name="g")]
            ),
            ToolMessage.create("ok", tool_name="f", tool_call_id="a"),
            ToolMessage(
                contents=[Content(text="boom", cache_control={"type": "ephemeral"})],
                tool_name="g",
                tool_call_id="b",
                failed=True,
            ),
        ]
    )

    assert request.messages[2] == {
        "role": "user",
        "content": [
            {
                "type": "tool_result",
                "tool_use_id": "a",
                "content": [{"type": "text", "text": "ok"}],
            },
            {
                "type": "tool_result",
                "tool_use_id": "b",
                "content": [{"type": "text", "text": "boom"}],
                "is_error": True,
                "cache_control": {"type": "ephemeral"},
            },
        ],
    }


async def test_consecutive_human_messages_are_merged(convert: Any) -> None:
    request = await convert([HumanMessage.create("A"), HumanMessage.create("B")])

    assert request.messages == [
        {
            "role": "user",
            "content": [{"type": "text", "text": "A"}, {"type": "text", "text": "B"}],
        }
    ]


async def test_thinking_blocks(
    capabilities: ChatCapabilities, run_context: RunContext
) -> None:
    block = {"type": "thinking", "thinking": "Hmm", "signature": "sig"}
    request = await to_anthropic_request(
        [
            HumanMessage.create("Hi"),
            AIMessage.create("Hello", tool_calls=[ToolCall(id="t", name="f")]),
            ToolMessage.create("ok", tool_name="f", tool_call_id="t"),
        ],
        model_name="claude-sonnet-5-5",
        capabilities=capabilities,
        media_converter=AnthropicChatProvider(AnthropicChatProviderSettings()),
        run_context=run_context,
        thinking_blocks={1: [block]},
    )

    assert request.messages[1]["content"][0] == block
    assert request.messages[1]["content"][1]["type"] == "text"
