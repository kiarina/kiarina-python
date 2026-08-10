from kiarina.agi.image_embedding_provider_impl.gemini import (
    create_gemini_image_embedding_provider,
)


def test_create_gemini_image_embedding_provider() -> None:
    _ = create_gemini_image_embedding_provider()
    assert True
