from kiarina.agi.base.token_utils import calc_audio_token


def test_calc_audio_token() -> None:
    assert calc_audio_token(1.0) == 32
