from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._helpers.normalize_file_segments import normalize_file_segments
    from ._models.base_file_segment_normalizer import BaseFileSegmentNormalizer
    from ._operations.create_file_segment_normalizer import (
        create_file_segment_normalizer,
    )
    from ._settings import FileSegmentNormalizerSettings, settings_manager
    from ._types.file_segment_normalizer import FileSegmentNormalizer

__all__ = [
    # ._helpers
    "normalize_file_segments",
    # ._models
    "BaseFileSegmentNormalizer",
    # ._operations
    "create_file_segment_normalizer",
    # ._settings
    "FileSegmentNormalizerSettings",
    "settings_manager",
    # ._types
    "FileSegmentNormalizer",
]


def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._helpers
        "normalize_file_segments": "._helpers.normalize_file_segments",
        # ._models
        "BaseFileSegmentNormalizer": "._models.base_file_segment_normalizer",
        # ._operations
        "create_file_segment_normalizer": "._operations.create_file_segment_normalizer",
        # ._settings
        "FileSegmentNormalizerSettings": "._settings",
        "settings_manager": "._settings",
        # ._types
        "FileSegmentNormalizer": "._types.file_segment_normalizer",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
