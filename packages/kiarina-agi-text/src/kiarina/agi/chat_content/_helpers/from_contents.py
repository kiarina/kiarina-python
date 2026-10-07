from kiarina.agi.chat_provider import ChatCapabilities
from kiarina.agi.content import Content
from kiarina.agi.message import MessageType
from kiarina.agi.run_context import RunContext

from .._models.media_converter import MediaConverter
from .._operations.from_content import from_content
from .._schemas.content_parts import ContentParts


async def from_contents(
    message_type: MessageType,
    contents: list[Content],
    *,
    capabilities: ChatCapabilities,
    media_converter: MediaConverter,
    run_context: RunContext,
) -> ContentParts:
    result = ContentParts()

    for content in contents:
        if content.payload:
            result.parts.append(content.payload)

        parts, purged_parts = (
            await from_content(
                message_type,
                content,
                capabilities=capabilities,
                media_converter=media_converter,
                run_context=run_context,
            )
        ).to_tuple()

        result.parts.extend(parts)
        result.purged_parts.extend(purged_parts)

    return result
