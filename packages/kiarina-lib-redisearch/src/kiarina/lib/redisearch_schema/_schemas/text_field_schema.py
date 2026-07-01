from typing import Literal

from pydantic import Field
from redis.commands.search.field import TextField

from .base_field_schema import BaseFieldSchema


class TextFieldSchema(BaseFieldSchema):
    """Schema for a text field."""

    type: Literal["text"] = Field(
        default="text",
        title="Field Type",
        description="RediSearch field type.",
    )
    weight: float = Field(
        default=1,
        title="Weight",
        description="Relative importance of the field in text search.",
    )
    no_stem: bool = Field(
        default=False,
        title="Disable Stemming",
        description="Index words without stemming.",
    )
    phonetic_matcher: str | None = Field(
        default=None,
        title="Phonetic Matcher",
        description="Phonetic matching algorithm.",
    )
    withsuffixtrie: bool = Field(
        default=False,
        title="Suffix Trie",
        description="Maintain a suffix trie for wildcard queries.",
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

    def to_field(self) -> TextField:
        return TextField(
            self.name,
            weight=self.weight,
            no_stem=self.no_stem,
            phonetic_matcher=self.phonetic_matcher,  # type: ignore
            sortable=self.sortable,
            no_index=self.no_index,
        )
