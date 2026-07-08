from kiarina.agi.vad_provider_impl.silero import create_silero_vad_provider


def test_create_silero_vad_provider() -> None:
    _ = create_silero_vad_provider(x=1)
    assert True
