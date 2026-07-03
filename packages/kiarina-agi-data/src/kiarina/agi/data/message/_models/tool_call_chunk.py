from pydantic import BaseModel


class ToolCallChunk(BaseModel):
    id: str | None = None
    name: str | None = None
    args: str | None = None
    index: int | None = None
