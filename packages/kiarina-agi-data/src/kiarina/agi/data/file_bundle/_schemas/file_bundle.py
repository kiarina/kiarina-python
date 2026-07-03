import json
import zipfile
from dataclasses import dataclass, field
from io import BytesIO
from typing import ClassVar, Self

from kiarina.utils.mime import MIMEBlob

from .._types.file_bundle_content_input import FileBundleContentInput
from .._types.file_bundle_file_path import FileBundleFilePath
from .file_bundle_manifest import FileBundleManifest
from .file_bundle_media_content import FileBundleMediaContent


@dataclass
class FileBundle:
    manifest: FileBundleManifest = field(default_factory=FileBundleManifest)
    files: dict[FileBundleFilePath, bytes] = field(default_factory=dict)

    MIME_TYPE: ClassVar[str] = "application/zip"

    def to_bytes(self) -> bytes:
        buffer = BytesIO()

        with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(
                FileBundleManifest.FILE_NAME,
                self.manifest.model_dump_json(),
            )

            for content in self.manifest.contents:
                if not isinstance(content, FileBundleMediaContent):
                    continue

                file_path = content.file_path

                if file_path not in self.files:
                    raise ValueError(
                        f"FileBundle.files is missing referenced file: {file_path!r}"
                    )

                zip_file.writestr(file_path, self.files[file_path])

        return buffer.getvalue()

    def to_mime_blob(self) -> MIMEBlob:
        return MIMEBlob(self.MIME_TYPE, self.to_bytes())

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        with zipfile.ZipFile(BytesIO(data)) as zip_file:
            try:
                raw_manifest = zip_file.read(FileBundleManifest.FILE_NAME)
            except KeyError as e:
                raise ValueError(
                    f"FileBundle is missing {FileBundleManifest.FILE_NAME}"
                ) from e

            manifest_dict = json.loads(raw_manifest.decode("utf-8"))

            if not isinstance(manifest_dict, dict):
                raise ValueError(
                    f"{FileBundleManifest.FILE_NAME} must contain a JSON object"
                )

            manifest = FileBundleManifest.model_validate(manifest_dict)

            files: dict[FileBundleFilePath, bytes] = {}

            for content in manifest.contents:
                if not isinstance(content, FileBundleMediaContent):
                    continue

                file_path = content.file_path

                if not _is_safe_zip_path(file_path):
                    raise ValueError(f"Unsafe file_path in manifest: {file_path!r}")

                try:
                    files[file_path] = zip_file.read(file_path)
                except KeyError as e:
                    raise ValueError(
                        f"FileBundle is missing referenced file: {file_path!r}"
                    ) from e

        return cls(manifest=manifest, files=files)

    @classmethod
    def from_mime_blob(cls, blob: MIMEBlob) -> Self:
        return cls.from_bytes(blob.raw_data)

    @classmethod
    def create(
        cls,
        manifest_contents: list[FileBundleContentInput],
        files: dict[FileBundleFilePath, bytes] | None = None,
    ) -> Self:
        return cls(
            manifest=FileBundleManifest.create(manifest_contents),
            files=files or {},
        )

    def __add__(self, other: Self) -> Self:
        if not isinstance(other, FileBundle):
            return NotImplemented

        duplicates = self.files.keys() & other.files.keys()

        if duplicates:
            raise ValueError(
                f"Cannot merge FileBundle: duplicate file paths {sorted(duplicates)!r}"
            )

        return type(self)(
            manifest=FileBundleManifest(
                contents=[*self.manifest.contents, *other.manifest.contents],
            ),
            files={**self.files, **other.files},
        )


def _is_safe_zip_path(file_path: str) -> bool:
    parts = file_path.replace("\\", "/").split("/")
    return not file_path.startswith("/") and ".." not in parts
