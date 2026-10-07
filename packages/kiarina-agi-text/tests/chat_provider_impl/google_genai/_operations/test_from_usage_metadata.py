from google.genai import types

from kiarina.agi.chat_provider_impl.google_genai._operations.from_usage_metadata import (
    from_usage_metadata,
)


def test_from_usage_metadata() -> None:
    usage = from_usage_metadata(
        types.GenerateContentResponseUsageMetadata(
            prompt_token_count=100,
            tool_use_prompt_token_count=10,
            cached_content_token_count=30,
            candidates_token_count=20,
            thoughts_token_count=5,
        )
    )

    assert usage is not None
    assert usage.prompt_tokens == 110
    assert usage.cached_input_tokens == 30
    assert usage.output_tokens == 25


def test_empty() -> None:
    usage = from_usage_metadata(types.GenerateContentResponseUsageMetadata())

    assert usage is not None
    assert (usage.prompt_tokens, usage.cached_input_tokens, usage.output_tokens) == (
        0,
        0,
        0,
    )
    assert from_usage_metadata(None) is None
