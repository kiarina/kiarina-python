from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._schemas.file_bundle import FileBundle
    from ._schemas.file_bundle_manifest import FileBundleManifest
    from ._schemas.file_bundle_media_content import FileBundleMediaContent
    from ._schemas.file_bundle_text_content import FileBundleTextContent
    from ._types.file_bundle_content import FileBundleContent
    from ._types.file_bundle_content_input import FileBundleContentInput
    from ._types.file_bundle_content_visibility import FileBundleContentVisibility
    from ._types.file_bundle_file_path import FileBundleFilePath
    from ._types.file_bundle_media_content_spec import FileBundleMediaContentSpec
    from ._types.file_bundle_media_content_type import FileBundleMediaContentType
    from ._types.file_bundle_text_content_spec import FileBundleTextContentSpec

__all__ = [
    # ._schemas
    "FileBundle",
    "FileBundleManifest",
    "FileBundleMediaContent",
    "FileBundleTextContent",
    # ._types
    "FileBundleContent",
    "FileBundleContentInput",
    "FileBundleContentVisibility",
    "FileBundleFilePath",
    "FileBundleMediaContentSpec",
    "FileBundleMediaContentType",
    "FileBundleTextContentSpec",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._schemas
        "FileBundle": "._schemas.file_bundle",
        "FileBundleManifest": "._schemas.file_bundle_manifest",
        "FileBundleMediaContent": "._schemas.file_bundle_media_content",
        "FileBundleTextContent": "._schemas.file_bundle_text_content",
        # ._types
        "FileBundleContent": "._types.file_bundle_content",
        "FileBundleContentInput": "._types.file_bundle_content_input",
        "FileBundleContentVisibility": "._types.file_bundle_content_visibility",
        "FileBundleFilePath": "._types.file_bundle_file_path",
        "FileBundleMediaContentSpec": "._types.file_bundle_media_content_spec",
        "FileBundleMediaContentType": "._types.file_bundle_media_content_type",
        "FileBundleTextContentSpec": "._types.file_bundle_text_content_spec",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
