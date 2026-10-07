from typing import Any

import pytest

from kiarina.agi.chat_provider import ChatCapabilities
from kiarina.agi.chat_provider_impl.google_genai import (
    GoogleGenAIChatProvider,
    GoogleGenAIChatProviderSettings,
)
from kiarina.agi.chat_provider_impl.google_genai._operations.to_google_genai_request import (
    to_google_genai_request,
)
from kiarina.agi.chat_provider_impl.google_genai._schemas.google_genai_request import (
    GoogleGenAIRequest,
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

SKIP = "skip_thought_signature_validator"


@pytest.fixture
def convert(capabilities: ChatCapabilities, run_context: RunContext) -> Any:
    async def convert(messages: list[Message]) -> GoogleGenAIRequest:
        return await to_google_genai_request(
            messages,
            capabilities=capabilities,
            media_converter=GoogleGenAIChatProvider(GoogleGenAIChatProviderSettings()),
            run_context=run_context,
        )

    return convert


async def test_conversation(convert: Any, messages: list[Message]) -> None:
    request = await convert([SystemMessage.create("Be kind."), *messages])

    assert request.system_instruction == "Be kind."
    assert [c.role for c in request.contents] == [
        "user",
        "model",
        "user",
        "model",
        "user",
        "model",
    ]

    call = request.contents[3].parts[0]
    assert call.function_call.name == "generate_image"
    assert call.function_call.args == {"instructions": "Create a image of a cat"}

    # The function response and the purged image share one user turn.
    tool_turn = request.contents[4].parts
    assert tool_turn[0].function_response.name == "generate_image"
    assert tool_turn[0].function_response.response == {"output": "image generated"}
    assert any(part.inline_data for part in tool_turn[1:])


async def test_thought_signature_bypass_in_active_loop(convert: Any) -> None:
    request = await convert(
        [
            HumanMessage.create("First"),
            AIMessage.create(tool_calls=[ToolCall(id="a", name="f")]),
            ToolMessage.create('{"ok": true}', tool_name="f", tool_call_id="a"),
            AIMessage.create("Done"),
            HumanMessage.create("Second"),
            AIMessage.create(
                tool_calls=[ToolCall(id="b", name="f"), ToolCall(id="c", name="f")]
            ),
            ToolMessage.create("1", tool_name="f", tool_call_id="b"),
            ToolMessage.create("2", tool_name="f", tool_call_id="c"),
        ]
    )

    old_call, new_call = request.contents[1], request.contents[5]

    assert old_call.parts[0].thought_signature is None
    assert new_call.parts[0].thought_signature == SKIP
    assert new_call.parts[1].thought_signature is None

    responses = request.contents[6].parts
    assert [p.function_response.response for p in responses] == [
        {"output": 1},
        {"output": 2},
    ]
    assert request.contents[2].parts[0].function_response.response == {"ok": True}


async def test_empty_and_unknown_parts(convert: Any) -> None:
    request = await convert(
        [
            HumanMessage.create(""),
            AIMessage(contents=[Content(payload={"type": "function_call"})]),
        ]
    )

    assert request.system_instruction is None
    assert request.contents[0].parts[0].text == ""
    assert request.contents[1].parts[0].text == ""


async def test_consecutive_human_messages_are_merged(convert: Any) -> None:
    request = await convert([HumanMessage.create("A"), HumanMessage.create("B")])

    assert len(request.contents) == 1
    assert [p.text for p in request.contents[0].parts] == ["A", "B"]
