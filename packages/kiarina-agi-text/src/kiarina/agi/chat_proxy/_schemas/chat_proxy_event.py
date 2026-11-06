from typing import Annotated, Literal

from pydantic import BaseModel, Field

from kiarina.agi.cost_record import CostRecord
from kiarina.agi.message import AIMessage, AIMessageChunk

from .chat_proxy_error_info import ChatProxyErrorInfo


class ChatProxyEvent(BaseModel):
    """
    One line of the chat proxy's NDJSON response: a chunk, the final message, a
    cost record, or an error. Cost records follow the final message.
    """

    type: Literal["chunk", "message", "cost", "error"] = Field(
        title="Type", description="What the event carries."
    )
    message: (
        Annotated[AIMessageChunk | AIMessage, Field(discriminator="type")] | None
    ) = Field(
        default=None,
        title="Message",
        description="The chunk or final message for `chunk` and `message`.",
    )
    cost_record: CostRecord | None = Field(
        default=None, title="Cost Record", description="The record for `cost`."
    )
    error: ChatProxyErrorInfo | None = Field(
        default=None, title="Error", description="The error for `error`."
    )
