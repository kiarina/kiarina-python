from kiarina.agi.scd_provider_impl.pyannote import (
    create_pyannote_scd_provider,
)


def test_create_pyannote_scd_provider() -> None:
    _ = create_pyannote_scd_provider(x=1)
    assert True
