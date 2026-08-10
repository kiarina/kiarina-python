from kiarina.agi.text_embedding_provider_impl.mock import (
    MockTextEmbeddingProvider,
    create_mock_text_embedding_provider,
)


def test_create_mock_text_embedding_provider() -> None:
    provider = create_mock_text_embedding_provider(dimension=2, embedding=[3.0, 4.0])

    assert isinstance(provider, MockTextEmbeddingProvider)
    assert provider.settings.dimension == 2
