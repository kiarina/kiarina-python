from typing import Any, Literal

from pydantic import Field
from redis.commands.search.field import VectorField

from .base_vector_field_schema import BaseVectorFieldSchema


class FlatVectorFieldSchema(BaseVectorFieldSchema):
    """Schema for a FLAT vector field."""

    algorithm: Literal["FLAT"] = Field(
        default="FLAT",
        title="Algorithm",
        description="Vector indexing algorithm.",
    )
    block_size: int | None = Field(
        default=None,
        title="Block Size",
        description="Number of vectors allocated in each memory block.",
    )

    # --------------------------------------------------
    # Public Methods
    # --------------------------------------------------

    def to_field(self) -> VectorField:
        return VectorField(self.name, self.algorithm, self._get_attributes())

    # --------------------------------------------------
    # Protected Methods
    # --------------------------------------------------

    def _get_attributes(self) -> dict[str, Any]:
        attributes = super()._get_attributes()

        if self.block_size is not None:
            attributes["BLOCK_SIZE"] = self.block_size

        return attributes
