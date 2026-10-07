from typing import Literal, TypeAlias

GoogleGenAIStopReason: TypeAlias = Literal["stop", "max_tokens", "safety"]
"""Why the model stopped, narrowed to what the provider acts on."""
