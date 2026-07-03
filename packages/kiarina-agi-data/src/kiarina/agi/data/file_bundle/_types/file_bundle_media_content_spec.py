from typing import NotRequired, TypedDict

from .file_bundle_content_visibility import FileBundleContentVisibility
from .file_bundle_file_path import FileBundleFilePath
from .file_bundle_media_content_type import FileBundleMediaContentType


class FileBundleMediaContentSpec(TypedDict):
    type: FileBundleMediaContentType
    file_path: FileBundleFilePath
    mime_type: str
    visibility: NotRequired[FileBundleContentVisibility]
