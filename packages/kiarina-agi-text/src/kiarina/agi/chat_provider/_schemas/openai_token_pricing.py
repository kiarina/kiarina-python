import math

from pydantic import BaseModel, Field


class OpenAITokenPricing(BaseModel):
    """
    OpenAI's per-token API pricing. The OpenAI provider charges with it, and the
    Codex provider records what its calls would cost on the API.
    """

    input_cost_microdollars_per_1k_tokens: int = 0

    cached_input_cost_microdollars_per_1k_tokens: int = 0

    output_cost_microdollars_per_1k_tokens: int = 0

    cache_write_cost_multiplier: float = Field(
        default=1.0,
        title="Cache Write Cost Multiplier",
        description="Multiplier applied to uncached input pricing for cache writes.",
    )

    extended_cost_threshold_tokens: int | None = Field(
        default=None,
        title="Extended Cost Threshold Tokens",
        description="Input token threshold above which extended pricing applies.",
    )

    extended_input_cost_multiplier: float = Field(
        default=1.0,
        title="Extended Input Cost Multiplier",
        description="Input cost multiplier applied above the extended cost threshold.",
    )

    extended_output_cost_multiplier: float = Field(
        default=1.0,
        title="Extended Output Cost Multiplier",
        description="Output cost multiplier applied above the extended cost threshold.",
    )

    def compute_cost(
        self,
        *,
        input_tokens: int,
        cache_write_tokens: int,
        cached_input_tokens: int,
        output_tokens: int,
    ) -> int:
        """
        The cost in microdollars. `input_tokens` excludes the cache writes and the
        cached input, which are priced on their own.
        """
        prompt_tokens = input_tokens + cache_write_tokens + cached_input_tokens

        input_multiplier = 1.0
        output_multiplier = 1.0
        threshold = self.extended_cost_threshold_tokens

        if threshold is not None and prompt_tokens > threshold:
            input_multiplier = self.extended_input_cost_multiplier
            output_multiplier = self.extended_output_cost_multiplier

        input_cost = self.input_cost_microdollars_per_1k_tokens * input_multiplier
        cached_input_cost = (
            self.cached_input_cost_microdollars_per_1k_tokens * input_multiplier
        )
        output_cost = self.output_cost_microdollars_per_1k_tokens * output_multiplier

        return math.ceil(
            input_cost * input_tokens / 1_000
            + input_cost * self.cache_write_cost_multiplier * cache_write_tokens / 1_000
            + cached_input_cost * cached_input_tokens / 1_000
            + output_cost * output_tokens / 1_000
        )
