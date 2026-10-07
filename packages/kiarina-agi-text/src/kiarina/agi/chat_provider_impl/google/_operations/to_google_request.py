import base64
import json
import logging
from collections.abc import Mapping
from typing import Any

from kiarina.agi.chat_content import ContentPart, MediaConverter, from_contents
from kiarina.agi.chat_provider import ChatCapabilities
from kiarina.agi.message import Message
from kiarina.agi.run_context import RunContext

from .._constants.skip_thought_signature import SKIP_THOUGHT_SIGNATURE
from .._schemas.google_request import GoogleRequest

try:
    from google.genai import types
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "google-genai is required to use GoogleChatProvider. "
        "Install it with: pip install 'kiarina-agi-text[chat-provider-google]'"
    ) from exc

logger = logging.getLogger(__name__)


async def to_google_request(
    messages: list[Message],
    *,
    capabilities: ChatCapabilities,
    media_converter: MediaConverter,
    run_context: RunContext,
    thought_signatures: Mapping[int, dict[str, Any]] | None = None,
) -> GoogleRequest:
    """
    Convert messages into Gemini's `system_instruction` and `contents`.

    - Consecutive human and tool messages are merged into one user turn, because
      the responses to parallel function calls must follow the call together.
    - `thought_signatures` by message index (`{"tool_calls": {id: base64},
      "text": base64}`) go back on those AI messages' parts.
    - Function calls in the active loop (after the last user turn with text or
      media) that have no signature carry the thought signature bypass.
    """
    request = GoogleRequest()
    system_texts: list[str] = []

    for index, message in enumerate(messages):
        result = await from_contents(
            message.type,
            message.contents,
            capabilities=capabilities,
            media_converter=media_converter,
            run_context=run_context,
        )

        if message.type == "system":
            system_texts += [
                str(part.get("text"))
                for part in result.parts
                if part.get("type") == "text" and part.get("text")
            ]
            continue

        if message.type == "ai":
            signatures = (thought_signatures or {}).get(index, {})
            parts = _to_parts(result.parts)
            text_parts = [part for part in parts if part.text]

            if text_parts and (signature := _decode(signatures.get("text"))):
                text_parts[-1].thought_signature = signature

            for tool_call in message.tool_calls:
                part = types.Part(
                    function_call=types.FunctionCall(
                        id=tool_call.id, name=tool_call.name, args=tool_call.args
                    )
                )

                if signature := _decode(
                    (signatures.get("tool_calls") or {}).get(tool_call.id)
                ):
                    part.thought_signature = signature

                parts.append(part)

            request.contents.append(
                types.Content(role="model", parts=parts or [types.Part(text="")])
            )
            continue

        if message.type == "human":
            parts = _to_parts(result.parts)

        elif message.type == "tool":
            parts = [
                types.Part(
                    function_response=types.FunctionResponse(
                        id=message.tool_call_id,
                        name=message.tool_name,
                        response=_to_function_response(result.parts),
                    )
                )
            ]
            parts += _to_parts(
                [p for p in result.parts if p.get("type") != "text"]
                + result.purged_parts
            )

        else:  # pragma: no cover
            raise AssertionError(f"Unsupported message type: {message.type}")

        last = request.contents[-1] if request.contents else None

        if last is not None and last.role == "user":
            last.parts = [*(last.parts or []), *parts]
        else:
            request.contents.append(
                types.Content(role="user", parts=parts or [types.Part(text="")])
            )

    if system_texts:
        request.system_instruction = "\n\n".join(system_texts)

    _skip_thought_signatures(request.contents)
    return request


def _decode(signature: Any) -> bytes | None:
    if not isinstance(signature, str) or not signature:
        return None

    try:
        return base64.b64decode(signature)
    except ValueError:
        return None


def _to_parts(parts: list[ContentPart]) -> list[Any]:
    """Unknown parts, such as LangChain blocks in old histories, are dropped."""
    result: list[Any] = []

    for part in parts:
        part_type = part.get("type")

        if part_type == "text":
            if text := part.get("text"):
                result.append(types.Part(text=str(text)))

        elif part_type == "inline_data":
            result.append(
                types.Part(
                    inline_data=types.Blob(
                        mime_type=part["mime_type"], data=part["data"]
                    )
                )
            )

        else:
            logger.debug("Dropped an unsupported content part: %s", part_type)

    return result


def _to_function_response(parts: list[ContentPart]) -> dict[str, Any]:
    text = "\n".join(
        str(part.get("text"))
        for part in parts
        if part.get("type") == "text" and part.get("text")
    )

    try:
        response = json.loads(text)
    except json.JSONDecodeError:
        response = text

    return response if isinstance(response, dict) else {"output": response}


def _skip_thought_signatures(contents: list[Any]) -> None:
    start = 0

    for index in range(len(contents) - 1, -1, -1):
        content = contents[index]

        parts = content.parts or []

        if (
            content.role == "user"
            and any(part.text or part.inline_data for part in parts)
            and not any(part.function_response for part in parts)
        ):
            start = index + 1
            break

    for content in contents[start:]:
        if content.role != "model":
            continue

        for part in content.parts or []:
            if part.function_call:
                if not part.thought_signature:
                    # NOTE: Assigned after construction so pydantic keeps the str.
                    # Bytes would be base64-encoded and hide the sentinel.
                    part.thought_signature = SKIP_THOUGHT_SIGNATURE
                break
