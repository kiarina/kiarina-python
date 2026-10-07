from kiarina.agi.chat_provider import ChatCapabilities
from kiarina.agi.chat_provider_impl.openai import OpenAIChatProviderSettings
from kiarina.agi.chat_provider_impl.openai._operations.to_responses_input import (
    to_responses_input,
)
from kiarina.agi.chat_provider_impl.openai._services.responses_endpoint import (
    ResponsesEndpoint,
)
from kiarina.agi.message import AIMessage, Message, SystemMessage
from kiarina.agi.run_context import RunContext


async def test_to_responses_input(
    messages: list[Message], capabilities: ChatCapabilities, run_context: RunContext
) -> None:
    items = await to_responses_input(
        [SystemMessage.create("Be kind."), *messages],
        capabilities=capabilities,
        media_converter=ResponsesEndpoint(OpenAIChatProviderSettings()),
        run_context=run_context,
    )

    assert [item.get("role") or item.get("type") for item in items] == [
        "system",
        "user",
        "assistant",
        "user",
        "function_call",
        "function_call_output",
        "user",
        "assistant",
    ]

    assert items[0]["content"] == "Be kind."
    assert items[4] == {
        "type": "function_call",
        "call_id": "123",
        "name": "generate_image",
        "arguments": '{"instructions": "Create a image of a cat"}',
    }
    assert items[5]["call_id"] == "123"
    assert any(part.get("type") == "input_image" for part in items[6]["content"])


async def test_ai_message_with_multiple_parts(
    capabilities: ChatCapabilities, run_context: RunContext
) -> None:
    items = await to_responses_input(
        [
            AIMessage.model_validate(
                {"contents": [{"text": "Hello"}, {"text": "World"}]}
            )
        ],
        capabilities=capabilities,
        media_converter=ResponsesEndpoint(OpenAIChatProviderSettings()),
        run_context=run_context,
    )

    assert items == [
        {
            "role": "assistant",
            "content": [
                {"type": "output_text", "text": "Hello"},
                {"type": "output_text", "text": "World"},
            ],
        }
    ]
