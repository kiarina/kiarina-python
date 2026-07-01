from typing import Literal

from pydantic import Field
from redis.commands.search.field import TagField

from .base_field_schema import BaseFieldSchema


class TagFieldSchema(BaseFieldSchema):
    """Schema for a tag field."""

    type: Literal["tag"] = Field(
        default="tag",
        title="Field Type",
        description="RediSearch field type.",
    )
    separator: str = Field(
        default=",",
        title="Separator",
        description="Character used to separate tags.",
    )
    case_sensitive: bool = Field(
        default=False,
        title="Case Sensitive",
        description="Preserve case when indexing and matching tags.",
    )
    no_index: bool = Field(
        default=False,
        title="Exclude from Index",
        description="Store the field without indexing it.",
    )
    sortable: bool | None = Field(
        default=False,
        title="Sortable",
        description="Allow results to be sorted by this field.",
    )
    multiple: bool = Field(
        default=False,
        exclude=True,
        title="Multiple Values",
        description="Decode stored values as multiple tags.",
    )

    def to_field(self) -> TagField:
        return TagField(
            self.name,
            separator=self.separator,
            case_sensitive=self.case_sensitive,
            sortable=self.sortable,
            no_index=self.no_index,
        )
