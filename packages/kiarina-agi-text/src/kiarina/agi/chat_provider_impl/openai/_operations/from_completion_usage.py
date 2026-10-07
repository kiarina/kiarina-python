from typing import TYPE_CHECKING

from .._schemas.openai_usage import OpenAIUsage

if TYPE_CHECKING:
    from openai.types import CompletionUsage


def from_completion_usage(usage: "CompletionUsage | None") -> OpenAIUsage | None:
    if usage is None:
        return None

    details = usage.prompt_tokens_details

    return OpenAIUsage(
        prompt_tokens=usage.prompt_tokens,
        cached_input_tokens=(details.cached_tokens or 0) if details else 0,
        cache_write_tokens=(details.cache_write_tokens or 0) if details else 0,
        output_tokens=usage.completion_tokens,
    )
