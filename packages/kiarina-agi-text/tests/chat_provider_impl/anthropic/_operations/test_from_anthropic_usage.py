import pytest
from anthropic.types import Usage

from kiarina.agi.chat_provider_impl.anthropic._operations.from_anthropic_usage import (
    from_anthropic_usage,
)


def test_with_breakdown() -> None:
    usage = from_anthropic_usage(
        Usage.model_validate(
            {
                "input_tokens": 10,
                "output_tokens": 5,
                "cache_read_input_tokens": 3,
                "cache_creation_input_tokens": 7,
                "cache_creation": {
                    "ephemeral_5m_input_tokens": 4,
                    "ephemeral_1h_input_tokens": 3,
                },
            }
        ),
        cache_ttl="5m",
    )

    assert usage.input_tokens == 10
    assert usage.cache_write_5m_tokens == 4
    assert usage.cache_write_1h_tokens == 3
    assert usage.cached_input_tokens == 3
    assert usage.output_tokens == 5


@pytest.mark.parametrize(("cache_ttl", "expected"), [("5m", (6, 0)), ("1h", (0, 6))])
def test_without_breakdown(cache_ttl: str, expected: tuple[int, int]) -> None:
    usage = from_anthropic_usage(
        Usage.model_validate(
            {"input_tokens": 1, "output_tokens": 1, "cache_creation_input_tokens": 6}
        ),
        cache_ttl=cache_ttl,  # type: ignore[arg-type]
    )

    assert (usage.cache_write_5m_tokens, usage.cache_write_1h_tokens) == expected
    assert usage.cached_input_tokens == 0
