from kiarina.agi.scd_provider_impl.mock import create_mock_scd_provider


def test_create_mock_scd_provider() -> None:
    _ = create_mock_scd_provider(x=1)
    assert True
