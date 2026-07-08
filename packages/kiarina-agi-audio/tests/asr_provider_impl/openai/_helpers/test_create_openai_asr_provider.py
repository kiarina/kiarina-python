from kiarina.agi.asr_provider_impl.openai import (
    OpenAIASRProvider,
    create_openai_asr_provider,
)


def test_create_openai_asr_provider() -> None:
    provider = create_openai_asr_provider(
        text_model_name="gpt-4o-mini-transcribe",
        text_input_cost_microdollars_per_1k_tokens=1_250,
        segments_model_name="gpt-4o-transcribe-diarize",
        segments_input_cost_microdollars_per_1k_tokens=2_500,
    )
    assert isinstance(provider, OpenAIASRProvider)
    assert provider.settings.text_model_name == "gpt-4o-mini-transcribe"
    assert provider.settings.text_input_cost_microdollars_per_1k_tokens == 1_250
    assert provider.settings.segments_model_name == "gpt-4o-transcribe-diarize"
    assert provider.settings.segments_input_cost_microdollars_per_1k_tokens == 2_500
