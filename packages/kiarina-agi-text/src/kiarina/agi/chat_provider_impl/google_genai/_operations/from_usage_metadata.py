from typing import Any

from .._schemas.google_genai_usage import GoogleGenAIUsage


def from_usage_metadata(usage_metadata: Any) -> GoogleGenAIUsage | None:
    """Take `GenerateContentResponseUsageMetadata`. In a stream, pass the last one."""
    if usage_metadata is None:
        return None

    return GoogleGenAIUsage(
        prompt_tokens=(usage_metadata.prompt_token_count or 0)
        + (usage_metadata.tool_use_prompt_token_count or 0),
        cached_input_tokens=usage_metadata.cached_content_token_count or 0,
        output_tokens=(usage_metadata.candidates_token_count or 0)
        + (usage_metadata.thoughts_token_count or 0),
    )
