from kiarina.agi.vad_provider_impl.mock import create_mock_vad_provider


def test_create_mock_vad_provider() -> None:
    _ = create_mock_vad_provider(x=1)
    assert True
