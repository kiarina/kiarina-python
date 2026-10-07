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
    - Media parts follow the element that marks them, so the conversation can be
      sent as parts in order, or as one text followed by the attachments.
    """
    transcript = Transcript()
    systems: list[str] = []
    media_count = 0

    for message in messages:
        result = await from_contents(
            message.type,
            message.contents,
            capabilities=capabilities,
            media_converter=media_converter,
            run_context=run_context,
        )
        text, media_parts = _to_text(result.parts + result.purged_parts, media_count)
        media_count += len(media_parts)
        elements: list[str] = []

        if message.type == "system":
            if not transcript.parts:
                systems.append(text)
            else:
                elements.append(_element("system_message", text))

        elif message.type == "human":
            elements.append(_element("human_message", text))

        elif message.type == "ai":
            if text:
                elements.append(_element("ai_message", text))

            for tool_call in message.tool_calls:
                elements.append(
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

            elements.append(_element("tool_result", text, **attrs))

        else:  # pragma: no cover
            raise AssertionError(f"Unsupported message type: {message.type}")

        transcript.parts += [{"type": "text", "text": e} for e in elements]
        transcript.parts += media_parts

    transcript.system = "\n\n".join(s for s in systems if s) or None
    return transcript


def _to_text(
    parts: list[ContentPart], media_offset: int
) -> tuple[str, list[ContentPart]]:
    texts: list[str] = []
    media_parts: list[ContentPart] = []

    for part in parts:
        if part.get("type") == "text":
            if text := str(part.get("text") or "").strip():
                texts.append(text)
        else:
            media_parts.append(part)
            texts.append(f'<attachment index="{media_offset + len(media_parts)}" />')

    return "\n\n".join(texts), media_parts


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
