from dataclasses import dataclass


@dataclass
class GoogleGenAIUsage:
    prompt_tokens: int = 0
    """All input tokens, including cached and tool-use prompt tokens."""

    cached_input_tokens: int = 0

    output_tokens: int = 0
    """Candidate and thought tokens, both billed as output."""
