from kiarina.agi.image_embedding_provider_impl.qwen3_vl import (
    create_qwen3_vl_image_embedding_provider,
)


def test_create_qwen3_vl_image_embedding_provider() -> None:
    _ = create_qwen3_vl_image_embedding_provider(base_url="http://localhost:8900")
    assert True
