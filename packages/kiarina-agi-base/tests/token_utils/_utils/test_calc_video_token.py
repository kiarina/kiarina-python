from kiarina.agi.token_utils import calc_video_token


def test_calc_video_token() -> None:
    assert calc_video_token(1.0) == 300
