from typing import Literal, TypeAlias

AnthropicStopReason: TypeAlias = Literal["stop", "max_tokens", "refusal"]
"""Why the model stopped, narrowed to what the provider acts on."""
