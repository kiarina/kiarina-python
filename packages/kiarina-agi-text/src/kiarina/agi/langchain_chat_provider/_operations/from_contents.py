from dataclasses import dataclass, field
from typing import cast

from kiarina.agi.chat_provider import ChatCapabilities
from kiarina.agi.content import Content
from kiarina.agi.message import MessageType
from kiarina.agi.run_context import RunContext

from .._models.langchain_media_converter import LangChainMediaConverter
from .._types.lc_content import LCContent
from .from_content import from_content


@dataclass
class Result:
    lc_contents: list[LCContent] = field(default_factory=list)
    purged_lc_contents: list[LCContent] = field(default_factory=list)

    @property
    def normalized_lc_contents(self) -> str | list[str | LCContent]:
        return _normalize_lc_content(self.lc_contents)

    @property
    def normalized_purged_lc_contents(self) -> str | list[str | LCContent]:
        return _normalize_lc_content(self.purged_lc_contents)


async def from_contents(
    message_type: MessageType,
    contents: list[Content],
    *,
    capabilities: ChatCapabilities,
    media_converter: LangChainMediaConverter,
    run_context: RunContext,
) -> Result:
    result = Result()

    for content in contents:
        if content.payload:
            result.lc_contents.append(content.payload)

        lc_contents, purged_lc_contents = (
            await from_content(
                message_type,
                content,
                capabilities=capabilities,
                media_converter=media_converter,
                run_context=run_context,
            )
        ).to_tuple()

        result.lc_contents.extend(lc_contents)
        result.purged_lc_contents.extend(purged_lc_contents)

    return result


def _normalize_lc_content(lc_contents: list[LCContent]) -> str | list[str | LCContent]:
    if not lc_contents:  # pragma: no cover
        return ""

    if (
        len(lc_contents) == 1
        and lc_contents[0].get("type") == "text"
        and lc_contents[0].get("cache_control") is None
    ):
        text = lc_contents[0].get("text")

        if isinstance(text, str):
            return text

    return cast(list[str | LCContent], lc_contents)
