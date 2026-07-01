from typing import Literal

from pydantic import Field
from redis.commands.search.field import NumericField

from .base_field_schema import BaseFieldSchema


class NumericFieldSchema(BaseFieldSchema):
    """Schema for a numeric field."""

    type: Literal["numeric"] = Field(
        default="numeric",
        title="Field Type",
        description="RediSearch field type.",
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

    # --------------------------------------------------
    # Public Methods
    # --------------------------------------------------

    def to_field(self) -> NumericField:
        return NumericField(
            self.name,
            sortable=self.sortable,
            no_index=self.no_index,
        )
