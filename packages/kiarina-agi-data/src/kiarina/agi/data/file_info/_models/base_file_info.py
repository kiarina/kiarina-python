import os
from datetime import datetime, timezone
from typing import Any, Self

import ulid
from pydantic import BaseModel, Field, field_validator

from kiarina.agi.data.chat_estimates import ChatEstimates
from kiarina.agi.file import URIOrFilePath
from kiarina.agi.file_utils import format_xml_attributes, is_uri
from kiarina.agi.run_context import get_node_id
from kiarina.agi.token_utils import TokenCount, calc_text_token

from .._types.file_id import FileID
from .._types.file_type import FileType
from .._types.group import Group
from .._types.unique_key import UniqueKey


class BaseFileInfo(BaseModel):
    type: FileType = Field(frozen=True)

    id: FileID = Field(default_factory=lambda: ulid.new().str)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    node_id: str = Field(default_factory=get_node_id)

    mime_type: str
    file_hash: str

    file_size: int
    token_count: TokenCount
    intermediate_file_path: str | None
    asset_uri: str | None

    uri_or_file_path: URIOrFilePath
    name: str = ""
    description: str = ""
    pinned: bool = False
    inline: bool = False
    metadata_only: bool = False
    content_only: bool = False
    no_merge: bool = False
    group: Group | None = None
    unique_key: UniqueKey | None = None
    keep_from_end: bool = False
    tag: str = "file"
    default_template: str = "<{tag}{attributes} />"
    metadata_only_template: str = '<{tag}{attributes} metadata_only="True" />'

    @field_validator("uri_or_file_path", mode="before")
    @classmethod
    def normalize_file_path(cls, v: str) -> str:
        if not is_uri(v):
            v = os.path.abspath(os.path.expanduser(os.path.expandvars(v)))
        return v

    @property
    def is_uri(self) -> bool:
        return is_uri(self.uri_or_file_path)

    @property
    def uri(self) -> str:
        if self.is_uri:
            return self.uri_or_file_path
        else:
            return f"file://{self.uri_or_file_path}"

    @property
    def prepared(self) -> bool:
        if self.asset_uri:
            return True
        if self.intermediate_file_path:
            return False
        if self.is_uri:
            return True

        return self.type not in ["image", "audio", "video", "pdf"]

    @property
    def xml_attributes(self) -> dict[str, Any]:
        attrs: dict[str, Any] = {
            "id": self.id,
            "name": self.name or None,
            "description": self.description or None,
            "uri": self.uri_or_file_path if self.is_uri else None,
            "file_path": self.uri_or_file_path if not self.is_uri else None,
        }

        return {k: v for k, v in attrs.items() if v}

    @property
    def optional_export_fields(self) -> tuple[str, ...]:
        return (
            "name",
            "description",
            "pinned",
            "inline",
            "metadata_only",
            "content_only",
            "no_merge",
            "group",
            "unique_key",
            "keep_from_end",
            "tag",
            "default_template",
            "metadata_only_template",
        )

    def export(self) -> dict[str, Any]:
        data = {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "uri_or_file_path": self.uri_or_file_path,
        }

        for field in self.optional_export_fields:
            if (value := self.get_value(field)) is not None:
                data[field] = value

        return data

    def to_estimates(self) -> ChatEstimates:
        if self.metadata_only:
            return self.to_metadata_estimates()
        elif self.content_only:
            return self.to_content_estimates()
        else:
            return self.to_metadata_estimates() + self.to_content_estimates()

    def to_metadata_estimates(self) -> ChatEstimates:
        estimates = ChatEstimates()
        estimates.add_token_count("text", calc_text_token(self.to_metadata_only_xml()))
        return estimates

    def to_content_estimates(self) -> ChatEstimates:
        return ChatEstimates()

    def to_xml(self, tag: str | None = None) -> str:
        return self.default_template.format(
            **self.model_dump(exclude={"tag"}, mode="json"),
            attributes=format_xml_attributes(self.xml_attributes),
            **{"tag": tag or self.tag},
        )

    def to_metadata_only_xml(self, tag: str | None = None) -> str:
        return self.metadata_only_template.format(
            **self.model_dump(exclude={"tag"}, mode="json"),
            attributes=format_xml_attributes(self.xml_attributes),
            **{"tag": tag or self.tag},
        )

    def as_metadata_only(self) -> Self:
        return self.model_copy(update={"metadata_only": True, "token_count": 0})

    def shrink(
        self, reduce: TokenCount, reserve: TokenCount = 0
    ) -> tuple[Self, TokenCount]:
        if self.metadata_only:
            return self, 0
        if self.token_count <= reserve:
            return self, 0
        reduce = min(reduce, self.token_count - reserve)
        return self._shrink(reduce)

    def _shrink(self, reduce: TokenCount) -> tuple[Self, TokenCount]:
        return self.as_metadata_only(), self.token_count

    def get_value(self, field_name: str, default: Any = None) -> Any:
        field_info = type(self).model_fields.get(field_name)

        if field_info is None:
            raise ValueError(
                f"Field '{field_name}' not found in model '{type(self).__name__}'"
            )

        value = getattr(self, field_name)

        if value == field_info.default:
            return default

        return value
