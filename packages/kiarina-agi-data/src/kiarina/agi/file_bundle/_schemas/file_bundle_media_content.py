from pydantic import BaseModel

from .._types.file_bundle_content_visibility import FileBundleContentVisibility
from .._types.file_bundle_file_path import FileBundleFilePath
from .._types.file_bundle_media_content_type import FileBundleMediaContentType


class FileBundleMediaContent(BaseModel):
    type: FileBundleMediaContentType
    file_path: FileBundleFilePath
    mime_type: str
    visibility: FileBundleContentVisibility = "always"
