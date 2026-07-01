from pydantic import BaseModel, Field

from ..schemas.document import Document


class SearchResult(BaseModel):
    """A result returned by a count, filter, or vector search."""

    total: int = Field(
        default=0,
        title="Total",
        description="Number of matching documents reported by RediSearch.",
    )
    duration: float = Field(
        default=0.0,
        title="Duration",
        description="Query execution time in milliseconds.",
    )
    documents: list[Document] = Field(
        default_factory=list,
        title="Documents",
        description="Documents returned for the requested page.",
    )
