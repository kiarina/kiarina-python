from typing import Literal, NotRequired, TypedDict

from .file_bundle_content_visibility import FileBundleContentVisibility


class FileBundleTextContentSpec(TypedDict):
    type: Literal["text"]
    text: str
    visibility: NotRequired[FileBundleContentVisibility]
