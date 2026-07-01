from typing import Any, Literal

from pydantic import Field
from redis.commands.search.field import VectorField

from .base_vector_field_schema import BaseVectorFieldSchema


class HNSWVectorFieldSchema(BaseVectorFieldSchema):
    """Schema for an HNSW vector field."""

    algorithm: Literal["HNSW"] = Field(
        default="HNSW",
        title="Algorithm",
        description="Vector indexing algorithm.",
    )
    m: int = Field(
        default=16,
        title="Maximum Connections",
        description="Maximum outgoing connections for each graph node.",
    )
    ef_construction: int = Field(
        default=200,
        title="Construction Candidate Count",
        description="Maximum candidate count used while building the index.",
    )
    ef_runtime: int = Field(
        default=10,
        title="Runtime Candidate Count",
        description="Maximum candidate count used while searching.",
    )
    epsilon: float = Field(
        default=0.01,
        title="Range Search Epsilon",
        description="Relative factor used to expand vector range searches.",
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

        attributes.update(
            {
                "M": self.m,
                "EF_CONSTRUCTION": self.ef_construction,
                "EF_RUNTIME": self.ef_runtime,
                "EPSILON": self.epsilon,
            }
        )

        return attributes
