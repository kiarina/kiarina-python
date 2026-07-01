from typing import Any, Self

from pydantic import BaseModel, Field as PydanticField
from redis.commands.search.field import Field as RedisearchField

from .._schemas.flat_vector_field_schema import FlatVectorFieldSchema
from .._schemas.hnsw_vector_field_schema import HNSWVectorFieldSchema
from .._types.field_schema import FieldSchema
from .._types.redisearch_field_dicts import RedisearchFieldDicts


class RedisearchSchema(BaseModel):
    """A RediSearch index schema."""

    fields: list[FieldSchema] = PydanticField(
        default_factory=list,
        title="Fields",
        description="Fields in the index.",
    )

    # --------------------------------------------------
    # Properties
    # --------------------------------------------------

    @property
    def field_names(self) -> list[str]:
        return [field.name for field in self.fields if field.name]

    @property
    def vector_field(self) -> FlatVectorFieldSchema | HNSWVectorFieldSchema:
        """Return the first vector field."""
        for field in self.fields:
            if field.type == "vector":
                return field

        raise ValueError("No vector field found")

    # --------------------------------------------------
    # Magic Methods
    # --------------------------------------------------

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, RedisearchSchema):
            return False

        return self.model_dump() == other.model_dump()

    # --------------------------------------------------
    # Public Methods
    # --------------------------------------------------

    def get_field(self, name: str) -> FieldSchema | None:
        for field in self.fields:
            if field.name == name:
                return field

        return None

    def to_fields(self) -> list[RedisearchField]:
        return [field.to_field() for field in self.fields]

    # --------------------------------------------------
    # Class Methods
    # --------------------------------------------------

    @classmethod
    def from_field_dicts(cls, field_dicts: RedisearchFieldDicts) -> Self:
        return cls.model_validate({"fields": field_dicts})
