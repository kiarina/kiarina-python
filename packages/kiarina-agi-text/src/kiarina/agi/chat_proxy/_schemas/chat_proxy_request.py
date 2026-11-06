from typing import Annotated

from pydantic import BaseModel, Field

from kiarina.agi.message import Message
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool_info import ToolChoice, ToolInfo

from .chat_proxy_file import ChatProxyFile


class ChatProxyRequest(BaseModel):
    """A chat request sent to the chat proxy, run there on the named chat model."""

    model_name: str = Field(
        title="Model Name",
        description="The chat model name or alias on the chat proxy.",
    )
    messages: list[Annotated[Message, Field(discriminator="type")]] = Field(
        title="Messages", description="The history to send."
    )
    tool_infos: list[ToolInfo] | None = Field(
        default=None, title="Tool Infos", description="The tools the model can call."
    )
    tool_choice: ToolChoice | None = Field(
        default=None, title="Tool Choice", description="How the model chooses tools."
    )
    parallel_tool_calls: bool | None = Field(
        default=None,
        title="Parallel Tool Calls",
        description="Whether the model can call tools in parallel.",
    )
    streaming: bool | None = Field(
        default=None, title="Streaming", description="Whether to stream chunks."
    )
    run_context: RunContext = Field(
        title="Run Context", description="The caller's run context."
    )
    files: dict[str, ChatProxyFile] = Field(
        default_factory=dict,
        title="Files",
        description=(
            "Media file contents keyed by the file's `asset_uri`, or its "
            "`uri_or_file_path` when it has none."
        ),
    )
