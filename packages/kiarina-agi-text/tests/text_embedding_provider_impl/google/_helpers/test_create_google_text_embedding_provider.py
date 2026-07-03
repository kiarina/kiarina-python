# mypy: ignore-errors

from kiarina.agi.text_embedding_provider_impl.google import (
    GoogleTextEmbeddingProvider,
    create_google_text_embedding_provider,
)


def test_create_google_text_embedding_provider() -> None:
    provider = create_google_text_embedding_provider(
        model_name="gemini-embedding-2",
        dimension=1536,
        google_auth_settings_key="api_key",
    )

    assert isinstance(provider, GoogleTextEmbeddingProvider)
    assert provider.settings.model_name == "gemini-embedding-2"
    assert provider.settings.dimension == 1536
    assert provider.settings.google_auth_settings_key == "api_key"
