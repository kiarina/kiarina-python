from typing import Any

from claude_agent_sdk import ResultMessage, TextBlock, ToolUseBlock

from kiarina.agi.content import Content
from kiarina.agi.message import AIMessage, ToolCall

from .._constants.tool_name_prefix import TOOL_NAME_PREFIX
from .._schemas.claude_code_chat_result import ClaudeCodeChatResult


def from_claude_agent_sdk_messages(
    content_blocks: list[Any],
    result_message: ResultMessage,
    *,
    parallel_tool_calls: bool,
) -> ClaudeCodeChatResult:
    """
    Build the model turn from the content blocks of its assistant messages.

    Claude Code sends each block as its own assistant message. Thinking blocks are
    dropped. Without parallel tool calls only the first tool call is kept, because
    Claude Code cannot be told to call one tool at a time.
    """
    texts: list[str] = []
    tool_calls: list[ToolCall] = []

    for block in content_blocks:
        if isinstance(block, TextBlock):
            texts.append(block.text)
        elif isinstance(block, ToolUseBlock):
            tool_calls.append(
                ToolCall(
                    id=block.id,
                    name=block.name.removeprefix(TOOL_NAME_PREFIX),
                    args=dict(block.input or {}),
                )
            )

    if not parallel_tool_calls:
        tool_calls = tool_calls[:1]

    return ClaudeCodeChatResult(
        ai_message=AIMessage(
            contents=[Content(text="".join(texts))], tool_calls=tool_calls
        ),
        stop_reason=result_message.stop_reason,
        usage=dict(result_message.usage or {}),
        total_cost_usd=result_message.total_cost_usd,
    )
