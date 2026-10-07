from dataclasses import dataclass

from kiarina.agi.message import AIMessage

from .._types.google_genai_stop_reason import GoogleGenAIStopReason
from .google_genai_usage import GoogleGenAIUsage


@dataclass
class GoogleGenAIChatResult:
    ai_message: AIMessage
    stop_reason: GoogleGenAIStopReason = "stop"
    usage: GoogleGenAIUsage | None = None
