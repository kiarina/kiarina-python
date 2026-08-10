from typing import Literal

EventType = Literal[
    "human_message",
    "ai_message",
    "ai_message_chunk",
    "tool_message",
    "custom",
]
"""
Event type

- "human_message": Human message
- "ai_message": LLM response message
- "ai_message_chunk": LLM response message chunk
- "tool_message": Tool message
- "custom": Custom data. Only lowercase letters and underscores are allowed
"""
