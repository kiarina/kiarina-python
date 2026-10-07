from typing import Literal, TypeAlias

OpenAIStopReason: TypeAlias = Literal["stop", "max_tokens", "content_filter"]
"""Why the model stopped, common to the Chat Completions and Responses APIs."""
