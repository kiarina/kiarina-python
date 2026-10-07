import json
from typing import Any

from kiarina.agi.chat_content import MediaConverter, from_contents
from kiarina.agi.chat_provider import ChatCapabilities
from kiarina.agi.message import Message
from kiarina.agi.run_context import RunContext

from .to_openai_parts import to_openai_parts


async def to_responses_input(
    messages: list[Message],
    *,
    capabilities: ChatCapabilities,
    media_converter: MediaConverter,
    run_context: RunContext,
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []

    for message in messages:
        result = await from_contents(
            message.type,
            message.contents,
            capabilities=capabilities,
            media_converter=media_converter,
            run_context=run_context,
        )

        if message.type == "system":
            items.append(
                {
                    "role": "system",
                    "content": to_openai_parts(result.parts, text_type="input_text"),
                }
            )

        elif message.type == "human":
            items.append(
                {
                    "role": "user",
                    "content": to_openai_parts(result.parts, text_type="input_text"),
                }
            )

        elif message.type == "ai":
            content = to_openai_parts(result.parts, text_type="output_text")

            if content:
                items.append({"role": "assistant", "content": content})

            for tool_call in message.tool_calls:
                items.append(
                    {
                        "type": "function_call",
                        "call_id": tool_call.id,
                        "name": tool_call.name,
                        "arguments": json.dumps(tool_call.args, ensure_ascii=False),
                    }
                )

        elif message.type == "tool":
            items.append(
                {
                    "type": "function_call_output",
                    "call_id": message.tool_call_id,
                    "output": to_openai_parts(result.parts, text_type="input_text"),
                }
            )

            if result.purged_parts:
                items.append(
                    {
                        "role": "user",
                        "content": to_openai_parts(
                            result.purged_parts, text_type="input_text"
                        ),
                    }
                )

        else:  # pragma: no cover
            raise AssertionError(f"Unsupported message type: {message.type}")

    return items
