from pydantic import BaseModel


class HelloToolSchema(BaseModel):
    """
    Print "Hello" for smoke testing.

    This tool takes no arguments.
    """
