import json

from kiarina.agi.chat_provider import ChatCapabilities
from kiarina.agi.message import Message
from kiarina.agi.run_context import RunContext

from .._models.media_converter import MediaConverter
from .._schemas.transcript import Transcript
from .._types.content_part import ContentPart
from .from_contents import from_contents


async def to_transcript(
    messages: list[Message],
    *,
    capabilities: ChatCapabilities,
    media_converter: MediaConverter,
    run_context: RunContext,
) -> Transcript:
    """
    Flatten messages into a system prompt and a `<messages>` XML prompt.

    - Leading system messages become `system`. A later one stays in place as
      `<system_message>`.
    - Media parts are moved to `media_parts` and marked in place, so the prompt
      can be sent as one text followed by the attachments.
    """
    transcript = Transcript()
    systems: list[str] = []
    lines: list[str] = []

    for message in messages:
        result = await from_contents(
            message.type,
            message.contents,
            capabilities=capabilities,
            media_converter=media_converter,
            run_context=run_context,
        )
        text = _to_text(result.parts + result.purged_parts, transcript.media_parts)

        if message.type == "system":
            if not lines:
                systems.append(text)
            else:
                lines.append(_element("system_message", text))

        elif message.type == "human":
            lines.append(_element("human_message", text))

        elif message.type == "ai":
            if text:
                lines.append(_element("ai_message", text))

            for tool_call in message.tool_calls:
                lines.append(
                    _element(
                        "tool_call",
                        json.dumps(tool_call.args, ensure_ascii=False),
                        id=tool_call.id,
                        name=tool_call.name,
                    )
                )

        elif message.type == "tool":
            attrs = {"id": message.tool_call_id, "name": message.tool_name}

            if message.failed:
                attrs["failed"] = "true"

            lines.append(_element("tool_result", text, **attrs))

        else:  # pragma: no cover
            raise AssertionError(f"Unsupported message type: {message.type}")

    transcript.system = "\n\n".join(s for s in systems if s) or None
    transcript.prompt = "\n".join(["<messages>", *lines, "</messages>"])
    return transcript


def _to_text(parts: list[ContentPart], media_parts: list[ContentPart]) -> str:
    texts: list[str] = []

    for part in parts:
        if part.get("type") == "text":
            if text := str(part.get("text") or "").strip():
                texts.append(text)
        else:
            media_parts.append(part)
            texts.append(f'<attachment index="{len(media_parts)}" />')

    return "\n\n".join(texts)


def _element(tag: str, text: str, **attrs: str) -> str:
    attr_text = "".join(f' {k}="{_escape_attr(v)}"' for k, v in attrs.items())
    return f"<{tag}{attr_text}>\n{text}\n</{tag}>"


def _escape_attr(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
