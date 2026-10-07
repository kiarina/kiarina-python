from typing import TYPE_CHECKING

from .._schemas.anthropic_usage import AnthropicUsage
from .._types.cache_ttl import CacheTTL

if TYPE_CHECKING:
    from anthropic.types import Usage


def from_anthropic_usage(usage: "Usage", *, cache_ttl: CacheTTL) -> AnthropicUsage:
    """
    Split cache writes by TTL. Without a breakdown, all writes are counted
    under the configured `cache_ttl`.
    """
    cache_write_tokens = usage.cache_creation_input_tokens or 0
    cache_write_5m_tokens = 0
    cache_write_1h_tokens = 0

    if usage.cache_creation:
        cache_write_5m_tokens = usage.cache_creation.ephemeral_5m_input_tokens
        cache_write_1h_tokens = usage.cache_creation.ephemeral_1h_input_tokens

    if cache_write_5m_tokens + cache_write_1h_tokens == 0:
        if cache_ttl == "5m":
            cache_write_5m_tokens = cache_write_tokens
        else:
            cache_write_1h_tokens = cache_write_tokens

    return AnthropicUsage(
        input_tokens=usage.input_tokens,
        cache_write_5m_tokens=cache_write_5m_tokens,
        cache_write_1h_tokens=cache_write_1h_tokens,
        cached_input_tokens=usage.cache_read_input_tokens or 0,
        output_tokens=usage.output_tokens,
    )
