from typing import Literal, TypeAlias

FileBundleMediaContentType: TypeAlias = Literal["image", "audio", "video", "pdf"]
"""
Media kind discriminator for :class:`FileBundleMediaContent`.

Mirrors the non-text members of :data:`kiarina.agi.file_info.FileType`.
"""
