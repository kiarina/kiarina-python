from pydantic import BaseModel, Field


class ExitToolSchema(BaseModel):
    """
    Output an error message and exit the program.

    Example:
    {
        "message": "Critical error occurred",
        "code": 1
    }
    """

    message: str = Field(description="Error message")
    code: int = Field(default=1, description="Exit code. Default is 1")
