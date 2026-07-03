# mypy: ignore-errors

from kiarina.agi.text_embedding_provider_impl.openai import (
    OpenAITextEmbeddingProvider,
    create_openai_text_embedding_provider,
)


def test_create_openai_text_embedding_provider() -> None:
    provider = create_openai_text_embedding_provider(
        model_name="text-embedding-3-small",
        dimension=1536,
    )

    assert isinstance(provider, OpenAITextEmbeddingProvider)
    assert provider.settings.model_name == "text-embedding-3-small"
    assert provider.settings.dimension == 1536


def test_create_openai_text_embedding_provider_for_openai_compatible_server() -> None:
    provider = create_openai_text_embedding_provider(
        model_name="Qwen3-Embedding-8B-mxfp8",
        openai_settings_key="omlx",
        dimension=4096,
    )

    assert isinstance(provider, OpenAITextEmbeddingProvider)
    assert provider.settings.model_name == "Qwen3-Embedding-8B-mxfp8"
    assert provider.settings.openai_settings_key == "omlx"
    assert provider.settings.dimension == 4096
