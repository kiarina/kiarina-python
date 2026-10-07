from typing import Literal, TypeAlias

GoogleStopReason: TypeAlias = Literal["stop", "max_tokens", "safety"]
"""Why the model stopped, narrowed to what the provider acts on."""
