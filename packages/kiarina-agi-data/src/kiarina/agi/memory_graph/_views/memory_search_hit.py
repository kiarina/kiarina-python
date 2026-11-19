from pydantic import BaseModel, Field

from kiarina.agi.memory import MemoryID


class MemorySearchHit(BaseModel):
    """A memory ID and its cosine similarity to the search query."""

    id: MemoryID = Field(title="Memory ID", description="ID of the matching memory.")
    score: float = Field(
        title="Score", description="Cosine similarity to the query vector."
    )
