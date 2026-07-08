from kiarina.agi.audio_embedding_provider_impl.clap_onnx import (
    create_clap_onnx_audio_embedding_provider,
)


def test_create_clap_onnx_audio_embedding_provider() -> None:
    _ = create_clap_onnx_audio_embedding_provider(model_path="dummy.onnx")
    assert True
