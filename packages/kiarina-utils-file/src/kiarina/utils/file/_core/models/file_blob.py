import os
from functools import cached_property
from typing import Self

from kiarina.utils.ext import extract_extension
from kiarina.utils.mime import MIMEBlob


class FileBlob:
    """File data with its path and MIME type."""

    def __init__(
        self,
        file_path: str | os.PathLike[str],
        mime_blob: MIMEBlob | None = None,
        *,
        mime_type: str | None = None,
        raw_data: bytes | None = None,
        raw_text: str | None = None,
    ):
        self._file_path: str = os.path.expanduser(
            os.path.expandvars(os.fspath(file_path))
        )

        if mime_blob is None:
            if mime_type is None:
                raise ValueError("mime_type must be provided if mime_blob is None")

            mime_blob = MIMEBlob(mime_type, raw_data, raw_text=raw_text)

        self._mime_blob: MIMEBlob = mime_blob

    def __str__(self) -> str:
        return f"FileBlob({self.file_path}, {self.mime_blob})"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, FileBlob)
            and self.file_path == other.file_path
            and self.mime_blob == other.mime_blob
        )

    @property
    def file_path(self) -> str:
        return self._file_path

    @property
    def mime_blob(self) -> MIMEBlob:
        return self._mime_blob

    @property
    def mime_type(self) -> str:
        return self.mime_blob.mime_type

    @property
    def raw_data(self) -> bytes:
        return self.mime_blob.raw_data

    @property
    def raw_text(self) -> str:
        return self.mime_blob.raw_text

    @property
    def raw_base64_str(self) -> str:
        return self.mime_blob.raw_base64_str

    @property
    def raw_base64_url(self) -> str:
        return self.mime_blob.raw_base64_url

    @property
    def hash_string(self) -> str:
        return self.mime_blob.hash_string

    @cached_property
    def ext(self) -> str:
        if ext := extract_extension(self.file_path):
            return ext

        return self.mime_blob.ext

    @property
    def hashed_file_name(self) -> str:
        return f"{self.hash_string}{self.ext}"

    def is_binary(self) -> bool:
        return self.mime_blob.is_binary()

    def is_text(self) -> bool:
        return self.mime_blob.is_text()

    def replace(
        self,
        *,
        file_path: str | os.PathLike[str] | None = None,
        mime_blob: MIMEBlob | None = None,
        mime_type: str | None = None,
        raw_data: bytes | None = None,
        raw_text: str | None = None,
    ) -> Self:
        mime_blob = mime_blob or self.mime_blob

        if mime_type is not None or raw_data is not None or raw_text is not None:
            mime_blob = mime_blob.replace(
                mime_type=mime_type,
                raw_data=raw_data,
                raw_text=raw_text,
            )

        return self.__class__(
            file_path=file_path or self.file_path,
            mime_blob=mime_blob,
        )
