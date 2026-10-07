from dataclasses import dataclass, field

from kiarina.agi.message import AIMessage

from .._types.google_genai_stop_reason import GoogleGenAIStopReason
from .google_genai_usage import GoogleGenAIUsage


@dataclass
class GoogleGenAIChatResult:
    ai_message: AIMessage
    stop_reason: GoogleGenAIStopReason = "stop"
    usage: GoogleGenAIUsage | None = None
    thought_signatures: dict[str, str] = field(default_factory=dict)
    """Thought signatures (base64) of the function calls, by tool call id."""
    text_thought_signature: str | None = None
    """The thought signature (base64) on the text, if any."""
