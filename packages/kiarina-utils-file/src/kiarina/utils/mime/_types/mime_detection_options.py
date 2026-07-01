from typing import NotRequired, TypedDict


class MimeDetectionOptions(TypedDict, total=False):
    mime_aliases: NotRequired[dict[str, str]]
    custom_mime_types: NotRequired[dict[str, str]]
    multi_extensions: NotRequired[set[str]]
    archive_extensions: NotRequired[set[str]]
    compression_extensions: NotRequired[set[str]]
    encryption_extensions: NotRequired[set[str]]
