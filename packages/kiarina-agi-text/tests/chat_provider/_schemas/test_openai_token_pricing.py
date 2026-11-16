from kiarina.agi.chat_model import ChatModelSettings
from kiarina.agi.chat_provider import OpenAITokenPricing

_PRICING_KEYS = set(OpenAITokenPricing.model_fields)


def test_compute_cost() -> None:
    pricing = OpenAITokenPricing(
        input_cost_microdollars_per_1k_tokens=2_000,
        cached_input_cost_microdollars_per_1k_tokens=100,
        output_cost_microdollars_per_1k_tokens=10_000,
        cache_write_cost_multiplier=1.25,
        extended_cost_threshold_tokens=272_000,
        extended_input_cost_multiplier=2.0,
        extended_output_cost_multiplier=1.5,
    )

    cost = pricing.compute_cost(
        input_tokens=1_000,
        cache_write_tokens=1_000,
        cached_input_tokens=10_000,
        output_tokens=100,
    )
    assert cost == 2_000 + 2_500 + 1_000 + 1_000

    extended = pricing.compute_cost(
        input_tokens=200_000,
        cache_write_tokens=0,
        cached_input_tokens=100_000,
        output_tokens=1_000,
    )
    assert extended == 800_000 + 20_000 + 15_000


def test_unpriced_costs_nothing() -> None:
    assert (
        OpenAITokenPricing().compute_cost(
            input_tokens=1_000,
            cache_write_tokens=1_000,
            cached_input_tokens=1_000,
            output_tokens=1_000,
        )
        == 0
    )


def test_codex_presets_price_as_the_openai_api() -> None:
    presets = ChatModelSettings().presets
    codex = {
        name: config
        for name, config in presets.items()
        if config.provider_name == "codex"
    }

    assert codex
    for name, config in codex.items():
        api = presets[config.provider_config["model_name"]]
        assert api.provider_name == "openai"
        assert {
            k: v for k, v in config.provider_config.items() if k in _PRICING_KEYS
        } == {k: v for k, v in api.provider_config.items() if k in _PRICING_KEYS}, name
