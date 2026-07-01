from typing import Any

from pydantic import BaseModel, Field


class Document(BaseModel):
    """A document returned by RediSearch."""

    key: str = Field(
        default="",
        title="Redis Key",
        description="Full Redis key for the document.",
    )
    id: str = Field(
        default="",
        title="Document ID",
        description="Document identifier without the configured key prefix.",
    )
    score: float = Field(
        default=0.0,
        title="Score",
        description="Similarity score returned by a vector search.",
    )
    mapping: dict[str, Any] = Field(
        default_factory=dict,
        title="Fields",
        description="Document fields.",
    )
