from kiarina.agi.audio_tagging_provider_impl.yamnet import (
    create_yamnet_audio_tagging_provider,
)


def test_create_yamnet_audio_tagging_provider() -> None:
    _ = create_yamnet_audio_tagging_provider(
        model_path="dummy.tflite",
        class_map_path="dummy.csv",
    )
    assert True
