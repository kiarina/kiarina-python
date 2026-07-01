from typing import Any, Literal

import numpy as np
from pydantic import Field

from .base_field_schema import BaseFieldSchema


class BaseVectorFieldSchema(BaseFieldSchema):
    """Base schema for a vector field."""

    type: Literal["vector"] = Field(
        default="vector",
        title="Field Type",
        description="RediSearch field type.",
    )
    dims: int = Field(
        title="Dimensions",
        description="Number of vector dimensions.",
    )
    datatype: Literal["FLOAT32", "FLOAT64"] = Field(
        default="FLOAT32",
        title="Data Type",
        description="Numeric type used to store vector elements.",
    )
    distance_metric: Literal["L2", "COSINE", "IP"] = Field(
        default="COSINE",
        title="Distance Metric",
        description="Metric used to compare vectors.",
    )
    initial_cap: int | None = Field(
        default=None,
        title="Initial Capacity",
        description="Initial vector index capacity.",
    )

    # --------------------------------------------------
    # Properties
    # --------------------------------------------------

    @property
    def dtype(self) -> Any:
        if self.datatype == "FLOAT32":
            return np.float32
        elif self.datatype == "FLOAT64":
            return np.float64
        else:
            raise ValueError(f"Unsupported datatype: {self.datatype}")

    # --------------------------------------------------
    # Protected Methods
    # --------------------------------------------------

    def _get_attributes(self) -> dict[str, Any]:
        attributes = {
            "TYPE": self.datatype,
            "DIM": self.dims,
            "DISTANCE_METRIC": self.distance_metric,
        }

        if self.initial_cap is not None:
            attributes["INITIAL_CAP"] = self.initial_cap

        return attributes
