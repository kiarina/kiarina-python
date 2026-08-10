from kiarina.agi.token_utils import calc_text_token


def test_calc_text_token() -> None:
    text = "Hello, world!"
    token_count = calc_text_token(text)
    assert token_count > 0
