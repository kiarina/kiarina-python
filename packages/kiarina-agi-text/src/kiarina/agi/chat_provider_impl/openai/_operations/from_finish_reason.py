from .._types.openai_stop_reason import OpenAIStopReason


def from_finish_reason(finish_reason: str | None) -> OpenAIStopReason:
    if finish_reason == "length":
        return "max_tokens"

    if finish_reason == "content_filter":
        return "content_filter"

    return "stop"
