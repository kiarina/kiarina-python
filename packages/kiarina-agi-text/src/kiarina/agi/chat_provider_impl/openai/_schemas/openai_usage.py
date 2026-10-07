from dataclasses import dataclass


@dataclass
class OpenAIUsage:
    prompt_tokens: int
    """All input tokens, including cached and cache-written tokens."""

    cached_input_tokens: int = 0
    cache_write_tokens: int = 0
    output_tokens: int = 0
