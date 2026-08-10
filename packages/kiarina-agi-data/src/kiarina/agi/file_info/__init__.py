from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.deduplicate_file_infos import deduplicate_file_infos
    from ._helpers.detect_file_type import detect_file_type
    from ._helpers.shrink_file_infos import shrink_file_infos
    from ._models.audio_file_info import AudioFileInfo
    from ._models.base_file_info import BaseFileInfo
    from ._models.image_file_info import ImageFileInfo
    from ._models.other_file_info import OtherFileInfo
    from ._models.pdf_file_info import PDFFileInfo
    from ._models.text_file_info import TextFileInfo
    from ._models.video_file_info import VideoFileInfo
    from ._types.file_id import FileID
    from ._types.file_info import FileInfo
    from ._types.file_type import FileType
    from ._types.group import Group
    from ._types.unique_key import UniqueKey

__all__ = [
    # ._helpers
    "deduplicate_file_infos",
    "detect_file_type",
    "shrink_file_infos",
    # ._models
    "AudioFileInfo",
    "BaseFileInfo",
    "ImageFileInfo",
    "OtherFileInfo",
    "PDFFileInfo",
    "TextFileInfo",
    "VideoFileInfo",
    # ._types
    "FileID",
    "FileInfo",
    "FileType",
    "Group",
    "UniqueKey",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._helpers
        "deduplicate_file_infos": "._helpers.deduplicate_file_infos",
        "detect_file_type": "._helpers.detect_file_type",
        "shrink_file_infos": "._helpers.shrink_file_infos",
        # ._models
        "AudioFileInfo": "._models.audio_file_info",
        "BaseFileInfo": "._models.base_file_info",
        "ImageFileInfo": "._models.image_file_info",
        "OtherFileInfo": "._models.other_file_info",
        "PDFFileInfo": "._models.pdf_file_info",
        "TextFileInfo": "._models.text_file_info",
        "VideoFileInfo": "._models.video_file_info",
        # ._types
        "FileID": "._types.file_id",
        "FileInfo": "._types.file_info",
        "FileType": "._types.file_type",
        "Group": "._types.group",
        "UniqueKey": "._types.unique_key",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
