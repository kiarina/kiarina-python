from kiarina.agi.audio_embedding_provider_impl.ecapa_tdnn_onnx import (
    create_ecapa_tdnn_onnx_audio_embedding_provider,
)


def test_create_ecapa_tdnn_onnx_audio_embedding_provider() -> None:
    _ = create_ecapa_tdnn_onnx_audio_embedding_provider(model_path="dummy.onnx")
    assert True
