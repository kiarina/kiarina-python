from .._types.google_genai_stop_reason import GoogleGenAIStopReason

_SAFETY_FINISH_REASONS = {
    "SAFETY",
    "RECITATION",
    "BLOCKLIST",
    "PROHIBITED_CONTENT",
    "SPII",
    "IMAGE_SAFETY",
    "IMAGE_PROHIBITED_CONTENT",
    "IMAGE_RECITATION",
}


def from_finish_reason(
    finish_reason: str | None, *, prompt_blocked: bool = False
) -> GoogleGenAIStopReason:
    if prompt_blocked or finish_reason in _SAFETY_FINISH_REASONS:
        return "safety"

    if finish_reason == "MAX_TOKENS":
        return "max_tokens"

    return "stop"
