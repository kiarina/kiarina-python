from typing import NotRequired, TypedDict

from kiarina.agi.file import URIOrFilePath
from kiarina.agi.file_info import FileID


class FileInfoSpec(TypedDict):
    id: NotRequired[FileID]
    created_at: NotRequired[str]  # ISO format
    uri_or_file_path: URIOrFilePath
    name: NotRequired[str]
    description: NotRequired[str]
    pinned: NotRequired[bool]
    inline: NotRequired[bool]
    metadata_only: NotRequired[bool]
    content_only: NotRequired[bool]
    no_merge: NotRequired[bool]
    group: NotRequired[str | None]
    unique_key: NotRequired[str | None]
    keep_from_end: NotRequired[bool]
    tag: NotRequired[str]
    default_template: NotRequired[str]
    metadata_only_template: NotRequired[str]

    # text
    start_line: NotRequired[int]
    end_line: NotRequired[int]

    # audio, video
    start_time: NotRequired[float]
    end_time: NotRequired[float]

    # pdf
    start_page: NotRequired[int]
    end_page: NotRequired[int]
