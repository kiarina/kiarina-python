import json
from typing import Any

from kiarina.agi.chat_content import MediaConverter, from_contents
from kiarina.agi.chat_provider import ChatCapabilities
from kiarina.agi.message import Message
from kiarina.agi.run_context import RunContext

from .to_openai_parts import to_openai_parts


async def to_chat_completions_messages(
    messages: list[Message],
    *,
    capabilities: ChatCapabilities,
    media_converter: MediaConverter,
    run_context: RunContext,
) -> list[dict[str, Any]]:
    openai_messages: list[dict[str, Any]] = []

    for message in messages:
        result = await from_contents(
            message.type,
            message.contents,
            capabilities=capabilities,
            media_converter=media_converter,
            run_context=run_context,
        )

        content = to_openai_parts(result.parts)

        if message.type == "system":
            openai_messages.append({"role": "system", "content": content})

        elif message.type == "human":
            openai_messages.append({"role": "user", "content": content})

        elif message.type == "ai":
            openai_message: dict[str, Any] = {"role": "assistant", "content": content}

            if message.tool_calls:
                openai_message["content"] = content or None
                openai_message["tool_calls"] = [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.name,
                            "arguments": json.dumps(tool_call.args, ensure_ascii=False),
                        },
                    }
                    for tool_call in message.tool_calls
                ]

            openai_messages.append(openai_message)

        elif message.type == "tool":
            openai_messages.append(
                {
                    "role": "tool",
                    "tool_call_id": message.tool_call_id,
                    "content": content,
                }
            )

            if result.purged_parts:
                openai_messages.append(
                    {"role": "user", "content": to_openai_parts(result.purged_parts)}
                )

        else:  # pragma: no cover
            raise AssertionError(f"Unsupported message type: {message.type}")

    return openai_messages
