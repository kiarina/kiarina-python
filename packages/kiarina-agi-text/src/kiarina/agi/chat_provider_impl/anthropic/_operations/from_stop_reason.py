from .._types.anthropic_stop_reason import AnthropicStopReason


def from_stop_reason(stop_reason: str | None) -> AnthropicStopReason:
    """`model_context_window_exceeded` stops the output, like `max_tokens`."""
    if stop_reason in ("max_tokens", "model_context_window_exceeded"):
        return "max_tokens"

    if stop_reason == "refusal":
        return "refusal"

    return "stop"
