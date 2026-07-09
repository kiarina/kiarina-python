from pydantic import BaseModel, Field


class WaitToolSchema(BaseModel):
    """
    Wait for the specified time.

    Example:
    {
        "wait_time": 5.0
    }
    """

    wait_time: float = Field(description="Wait time (seconds)")
