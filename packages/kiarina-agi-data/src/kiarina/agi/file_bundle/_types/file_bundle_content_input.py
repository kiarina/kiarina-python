from typing import TypeAlias

from .file_bundle_content import FileBundleContent
from .file_bundle_media_content_spec import FileBundleMediaContentSpec
from .file_bundle_text_content_spec import FileBundleTextContentSpec

FileBundleContentInput: TypeAlias = (
    str | FileBundleTextContentSpec | FileBundleMediaContentSpec | FileBundleContent
)
