import pytest

from kiarina.agi.chat_content import MediaConverter
from kiarina.agi.chat_provider import ChatCapabilities
from kiarina.agi.chat_provider_impl.codex_app_server._operations.to_thread_items import (
    to_thread_items,
)
from kiarina.agi.file_info import ImageFileInfo
from kiarina.agi.message import (
    AIMessage,
    HumanMessage,
    Message,
    SystemMessage,
    ToolCall,
    ToolMessage,
)
from kiarina.agi.run_context import RunContext

_IMAGE = {"type": "image", "mime_type": "image/png"}


async def test_to_thread_items(
    capabilities: ChatCapabilities,
    media_converter: MediaConverter,
    run_context: RunContext,
    image_file_info: ImageFileInfo,
) -> None:
    request = await to_thread_items(
        [
            SystemMessage.create("Be brief."),
            HumanMessage.create("Weather?", files=[image_file_info]),
            AIMessage.create(
                "Checking.",
                tool_calls=[
                    ToolCall(id="call_1", name="get_weather", args={"c": "名"})
                ],
            ),
            ToolMessage.create("rain", tool_name="get_weather", tool_call_id="call_1"),
            ToolMessage.create(
                "", [image_file_info], tool_name="get_map", tool_call_id="call_2"
            ),
            AIMessage.create(),
            SystemMessage.create("Answer in English."),
        ],
        tool_choice=None,
        capabilities=capabilities,
        media_converter=media_converter,
        run_context=run_context,
    )

    assert request.instructions == "Be brief."
    user, assistant, call, output, image_output, purged, developer = request.items
    assert user["role"] == "user"
    assert _IMAGE in user["content"]
    assert user["content"][-1] == {"type": "input_text", "text": "Weather?"}
    assert assistant == {
        "type": "message",
        "role": "assistant",
        "content": [{"type": "output_text", "text": "Checking."}],
    }
    assert call == {
        "type": "function_call",
        "call_id": "call_1",
        "name": "get_weather",
        "arguments": '{"c": "名"}',
    }
    assert output == {
        "type": "function_call_output",
        "call_id": "call_1",
        "output": "rain",
    }
    assert image_output["call_id"] == "call_2"
    assert purged["role"] == "user"
    assert _IMAGE in purged["content"]
    assert developer == {
        "type": "message",
        "role": "developer",
        "content": [{"type": "input_text", "text": "Answer in English."}],
    }


@pytest.mark.parametrize(
    ("tool_choice", "instruction"),
    [
        ("auto", None),
        ("any", "You must respond by calling one of the provided tools."),
        ("search", "You must respond by calling the `search` tool."),
    ],
)
async def test_to_thread_items_tool_choice(
    tool_choice: str,
    instruction: str | None,
    capabilities: ChatCapabilities,
    media_converter: MediaConverter,
    run_context: RunContext,
) -> None:
    messages: list[Message] = [HumanMessage.create("Hi")]
    request = await to_thread_items(
        messages,
        tool_choice=tool_choice,
        capabilities=capabilities,
        media_converter=media_converter,
        run_context=run_context,
    )

    assert request.instructions is None
    assert request.items[0]["content"] == [{"type": "input_text", "text": "Hi"}]

    if instruction:
        assert request.items[-1] == {
            "type": "message",
            "role": "developer",
            "content": [{"type": "input_text", "text": instruction}],
        }
    else:
        assert len(request.items) == 1
