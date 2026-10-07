from dataclasses import dataclass, field

from kiarina.agi.chat_provider import ChatCapabilities
from kiarina.agi.content import Content
from kiarina.agi.message import MessageType
from kiarina.agi.run_context import RunContext

from .._models.media_converter import MediaConverter
from .._types.content_part import ContentPart
from .from_file_info import from_file_info


@dataclass
class Result:
    parts: list[ContentPart] = field(default_factory=list)
    purged_parts: list[ContentPart] = field(default_factory=list)

    def to_tuple(self) -> tuple[list[ContentPart], list[ContentPart]]:
        return self.parts, self.purged_parts


async def from_content(
    message_type: MessageType,
    content: Content,
    *,
    capabilities: ChatCapabilities,
    media_converter: MediaConverter,
    run_context: RunContext,
) -> Result:
    result = Result()
    mergeable_texts: list[str] = []

    for file_info in content.files:
        tag = content.file_tags.get(file_info.type)

        text, media_dicts = (
            await from_file_info(
                file_info,
                tag=tag,
                capabilities=capabilities,
                media_converter=media_converter,
                run_context=run_context,
            )
        ).to_tuple()

        # should wrap
        if text and media_dicts:
            text = content.to_xml(text)

        # should merge
        if not file_info.no_merge and text and not media_dicts:
            mergeable_texts.append(text)
            continue

        _flush_mergeable_texts(mergeable_texts, content, result)

        # should purge
        if (
            message_type == "tool"
            and not capabilities.can_include("tool", file_info.type)
            and capabilities.can_include("human", file_info.type)
        ):
            if text:
                result.purged_parts.append({"type": "text", "text": text})
            if media_dicts:
                result.purged_parts.extend(media_dicts)
        else:
            if text:
                result.parts.append({"type": "text", "text": text})
            if media_dicts:
                result.parts.extend(media_dicts)

    _flush_mergeable_texts(mergeable_texts, content, result)

    if content.text:
        result.parts.append(
            {
                "type": "text",
                "text": content.text,
            }
        )

    _apply_cache_control(content, result)

    return result


def _flush_mergeable_texts(
    mergeable_texts: list[str],
    text_files_content: Content,
    result: Result,
) -> None:
    if mergeable_texts:
        result.parts.append(
            {
                "type": "text",
                "text": text_files_content.to_xml("\n".join(mergeable_texts).strip()),
            }
        )
        mergeable_texts.clear()


def _apply_cache_control(
    text_files_content: Content,
    result: Result,
) -> None:
    if cache_control := text_files_content.cache_control:
        if result.purged_parts:
            result.purged_parts[-1]["cache_control"] = cache_control
        elif result.parts:
            result.parts[-1]["cache_control"] = cache_control
