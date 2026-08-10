from kiarina.agi.image_embedding_provider_impl.siglip2 import (
    create_siglip2_image_embedding_provider,
)


def test_create_siglip2_image_embedding_provider() -> None:
    _ = create_siglip2_image_embedding_provider(model_path="dummy.onnx")
    assert True
