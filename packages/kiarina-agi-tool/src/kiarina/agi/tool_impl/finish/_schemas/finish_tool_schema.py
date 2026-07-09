from pydantic import BaseModel


class FinishToolSchema(BaseModel):
    """
    Finish the task.

    Use this tool when the task is completed successfully.
    """
