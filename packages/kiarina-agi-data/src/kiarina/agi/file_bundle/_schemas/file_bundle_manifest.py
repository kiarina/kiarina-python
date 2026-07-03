from typing import ClassVar, Self

from pydantic import BaseModel, Field, TypeAdapter

from .._types.file_bundle_content import FileBundleContent
from .._types.file_bundle_content_input import FileBundleContentInput
from .file_bundle_text_content import FileBundleTextContent

_CONTENT_ADAPTER: TypeAdapter[FileBundleContent] = TypeAdapter(FileBundleContent)


class FileBundleManifest(BaseModel):
    FILE_NAME: ClassVar[str] = "manifest.json"

    contents: list[FileBundleContent] = Field(default_factory=list)

    @classmethod
    def create(
        cls,
        contents: list[FileBundleContentInput],
    ) -> Self:
        normalized: list[FileBundleContent] = []

        for item in contents:
            if isinstance(item, str):
                normalized.append(FileBundleTextContent(text=item))
            elif isinstance(item, dict):
                normalized.append(_CONTENT_ADAPTER.validate_python(item))
            else:
                normalized.append(item)

        return cls(contents=normalized)
