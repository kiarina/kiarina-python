from collections.abc import Sequence
from typing import Any, NotRequired, TypedDict

from kiarina.agi.file_info import FileType
from kiarina.agi.file_info_loader import FileInfoInput


class ContentSpec(TypedDict):
    text: NotRequired[str]
    files: NotRequired[Sequence[FileInfoInput]]
    cache_control: NotRequired[dict[str, Any]]
    tag: NotRequired[str]
    description: NotRequired[str]
    template: NotRequired[str]
    file_tags: NotRequired[dict[FileType, str]]
