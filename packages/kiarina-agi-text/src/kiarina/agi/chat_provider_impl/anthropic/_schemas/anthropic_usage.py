from dataclasses import dataclass


@dataclass
class AnthropicUsage:
    input_tokens: int = 0
    """Uncached input tokens."""

    cache_write_5m_tokens: int = 0
    cache_write_1h_tokens: int = 0
    cached_input_tokens: int = 0
    output_tokens: int = 0
