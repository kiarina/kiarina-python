from typing import Literal

from pydantic import BaseModel

from .._types.file_bundle_content_visibility import FileBundleContentVisibility


class FileBundleTextContent(BaseModel):
    type: Literal["text"] = "text"
    text: str
    visibility: FileBundleContentVisibility = "always"
