from kiarina.agi.image_embedding_provider_impl.mock import (
    create_mock_image_embedding_provider,
)


def test_create_mock_image_embedding_provider() -> None:
    _ = create_mock_image_embedding_provider(embedding=[0.0, 2.0], dimension=2)
    assert True
