from typing import Literal, TypeAlias

FileBundleContentVisibility: TypeAlias = Literal["always", "supported", "unsupported"]
"""
Controls when a content item should be exposed to the consumer.

- ``always``: include regardless of the parent capability.
- ``supported``: include only when the parent file type is natively supported.
- ``unsupported``: include only when the parent file type is NOT natively supported
  (e.g. a transcript that substitutes for audio playback).
"""
