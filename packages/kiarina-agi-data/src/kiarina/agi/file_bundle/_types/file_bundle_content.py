from typing import Annotated, TypeAlias

from pydantic import Field

from .._schemas.file_bundle_media_content import FileBundleMediaContent
from .._schemas.file_bundle_text_content import FileBundleTextContent

FileBundleContent: TypeAlias = Annotated[
    FileBundleMediaContent | FileBundleTextContent,
    Field(discriminator="type"),
]
"""
A single entry in a :class:`FileBundleManifest`.

Either a media reference (file stored in the archive) or inline text.
Dispatch is keyed on the ``type`` field via Pydantic's discriminated union.
"""
