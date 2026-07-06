# mypy: disable-error-code="no-untyped-def,no-untyped-call,type-arg,attr-defined,no-any-return"

from kiarina.agi.image_embedding_provider_impl.sface import (
    create_sface_image_embedding_provider,
)


def test_create_sface_image_embedding_provider() -> None:
    _ = create_sface_image_embedding_provider(model_path="dummy.onnx")
    assert True
