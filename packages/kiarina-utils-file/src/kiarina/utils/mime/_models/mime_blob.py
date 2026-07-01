import base64
import hashlib
import logging
from functools import cached_property
from typing import Self

from kiarina.utils.encoding import (
    decode_binary_to_text,
    is_binary,
)
from kiarina.utils.ext import detect_extension

from .._settings import settings_manager

logger = logging.getLogger(__name__)


class MIMEBlob:
    """Binary data with its MIME type."""

    def __init__(
        self,
        mime_type: str,
        raw_data: bytes | None = None,
        *,
        raw_text: str | None = None,
    ):
        if not mime_type:
            raise ValueError("MIME type is required")

        if raw_data is None and raw_text is None:
            raise ValueError("Either raw_data or raw_text must be provided")

        if raw_data is not None and raw_text is not None:
            raise ValueError("Only one of raw_data or raw_text should be provided")

        if raw_data is None:
            raw_data = (raw_text or "").encode("utf-8", errors="replace")

        self._mime_type: str = mime_type

        self._raw_data: bytes = raw_data

        if raw_text is not None:
            self.__dict__["raw_text"] = raw_text

    def __str__(self) -> str:
        return f"MIMEBlob({self.mime_type}, {len(self.raw_data)} bytes)"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, MIMEBlob)
            and self.mime_type == other.mime_type
            and self.raw_data == other.raw_data
        )

    @property
    def mime_type(self) -> str:
        return self._mime_type

    @property
    def raw_data(self) -> bytes:
        return self._raw_data

    @cached_property
    def raw_text(self) -> str:
        return decode_binary_to_text(self.raw_data) if self.raw_data else ""

    @cached_property
    def raw_base64_str(self) -> str:
        return base64.b64encode(self.raw_data).decode("utf-8")

    @property
    def raw_base64_url(self) -> str:
        return f"data:{self.mime_type};base64,{self.raw_base64_str}"

    @cached_property
    def hash_string(self) -> str:
        hash_algorithm = settings_manager.settings.hash_algorithm

        if (h := getattr(hashlib, hash_algorithm, None)) is None:
            raise ValueError(f"Unsupported hash algorithm: {hash_algorithm}")

        hash_string = h(self.raw_data).hexdigest()
        assert isinstance(hash_string, str), "Hash string must be a string"
        return hash_string

    @cached_property
    def ext(self) -> str:
        return detect_extension(self.mime_type, default=".bin")

    @property
    def hashed_file_name(self) -> str:
        return f"{self.hash_string}{self.ext}"

    def is_binary(self) -> bool:
        return is_binary(self.raw_data)

    def is_text(self) -> bool:
        return not self.is_binary()

    def replace(
        self,
        *,
        mime_type: str | None = None,
        raw_data: bytes | None = None,
        raw_text: str | None = None,
    ) -> Self:
        if raw_data is not None and raw_text is not None:
            raise ValueError("Only one of raw_data or raw_text should be provided")

        if raw_data is None and raw_text is None:
            raw_data = self.raw_data

        return self.__class__(
            mime_type=mime_type or self.mime_type,
            raw_data=raw_data,
            raw_text=raw_text,
        )
