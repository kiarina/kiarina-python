from openai.types import CompletionUsage

from kiarina.agi.chat_provider_impl.openai._operations.from_completion_usage import (
    from_completion_usage,
)


def test_from_completion_usage() -> None:
    usage = from_completion_usage(
        CompletionUsage.model_validate(
            {
                "prompt_tokens": 100,
                "completion_tokens": 20,
                "total_tokens": 120,
                "prompt_tokens_details": {
                    "cached_tokens": 30,
                    "cache_write_tokens": 10,
                },
            }
        )
    )

    assert usage is not None
    assert usage.prompt_tokens == 100
    assert usage.cached_input_tokens == 30
    assert usage.cache_write_tokens == 10
    assert usage.output_tokens == 20


def test_without_details() -> None:
    usage = from_completion_usage(
        CompletionUsage(prompt_tokens=1, completion_tokens=2, total_tokens=3)
    )

    assert usage is not None
    assert usage.cached_input_tokens == 0


def test_none() -> None:
    assert from_completion_usage(None) is None
