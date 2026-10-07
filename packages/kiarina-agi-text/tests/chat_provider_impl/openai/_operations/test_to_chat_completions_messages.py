from kiarina.agi.chat_provider import ChatCapabilities
from kiarina.agi.chat_provider_impl.openai import OpenAIChatProviderSettings
from kiarina.agi.chat_provider_impl.openai._operations.to_chat_completions_messages import (
    to_chat_completions_messages,
)
from kiarina.agi.chat_provider_impl.openai._services.chat_completions_endpoint import (
    ChatCompletionsEndpoint,
)
from kiarina.agi.content import Content
from kiarina.agi.message import Message, SystemMessage
from kiarina.agi.run_context import RunContext


async def test_to_chat_completions_messages(
    messages: list[Message], capabilities: ChatCapabilities, run_context: RunContext
) -> None:
    openai_messages = await to_chat_completions_messages(
        [
            SystemMessage(
                contents=[Content(text="Be kind.", cache_control={"type": "ephemeral"})]
            ),
            *messages,
        ],
        capabilities=capabilities,
        media_converter=ChatCompletionsEndpoint(OpenAIChatProviderSettings()),
        run_context=run_context,
    )

    assert [m["role"] for m in openai_messages] == [
        "system",
        "user",
        "assistant",
        "user",
        "assistant",
        "tool",
        "user",
        "assistant",
    ]

    assert openai_messages[0]["content"] == "Be kind."
    assert openai_messages[1]["content"] == "Hello"

    assert openai_messages[4]["content"] is None
    assert openai_messages[4]["tool_calls"] == [
        {
            "id": "123",
            "type": "function",
            "function": {
                "name": "generate_image",
                "arguments": '{"instructions": "Create a image of a cat"}',
            },
        }
    ]

    # The tool message cannot include the image, so it moves to a user message.
    assert openai_messages[5]["tool_call_id"] == "123"
    assert "image generated" in str(openai_messages[5]["content"])
    assert any(
        part.get("type") == "image_url" for part in openai_messages[6]["content"]
    )
