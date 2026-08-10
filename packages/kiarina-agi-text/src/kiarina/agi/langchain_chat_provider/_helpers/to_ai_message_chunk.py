from kiarina.agi.message import AIMessageChunk, ToolCallChunk

from .._operations.to_contents import to_contents
from .._operations.to_tool_calls import to_tool_calls
from .._types.lc_ai_message_chunk import LCAIMessageChunk
from .._types.lc_tool_call_chunk import LCToolCallChunk


def to_ai_message_chunk(lc_ai_message: LCAIMessageChunk) -> AIMessageChunk:
    return AIMessageChunk(
        contents=to_contents(lc_ai_message.content),
        tool_calls=to_tool_calls(lc_ai_message.tool_calls),
        tool_call_chunks=_to_tool_call_chunks(lc_ai_message.tool_call_chunks),
    )


def _to_tool_call_chunks(
    lc_tool_call_chunks: list[LCToolCallChunk],
) -> list[ToolCallChunk]:
    return [
        ToolCallChunk(
            id=lc_tool_call_chunk.get("id"),
            name=lc_tool_call_chunk.get("name"),
            args=lc_tool_call_chunk.get("args"),
            index=lc_tool_call_chunk.get("index"),
        )
        for lc_tool_call_chunk in lc_tool_call_chunks
    ]
