from kiarina.agi.video_generation_provider_impl.openai import (
    OpenAIVideoGenerationProvider,
    create_openai_video_generation_provider,
)


def test_create_openai_video_generation_provider() -> None:
    provider = create_openai_video_generation_provider(model_name="sora-2")
    assert isinstance(provider, OpenAIVideoGenerationProvider)
    assert provider.settings.model_name == "sora-2"
