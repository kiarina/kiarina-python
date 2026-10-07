from dataclasses import dataclass, field
from typing import cast

from .._types.content_part import ContentPart


@dataclass
class ContentParts:
    parts: list[ContentPart] = field(default_factory=list)

    purged_parts: list[ContentPart] = field(default_factory=list)
    """Parts the tool message cannot include, to be sent in a following human message."""

    @property
    def normalized_parts(self) -> str | list[str | ContentPart]:
        return _normalize(self.parts)

    @property
    def normalized_purged_parts(self) -> str | list[str | ContentPart]:
        return _normalize(self.purged_parts)


def _normalize(parts: list[ContentPart]) -> str | list[str | ContentPart]:
    if not parts:  # pragma: no cover
        return ""

    if (
        len(parts) == 1
        and parts[0].get("type") == "text"
        and parts[0].get("cache_control") is None
    ):
        text = parts[0].get("text")

        if isinstance(text, str):
            return text

    return cast(list[str | ContentPart], parts)
