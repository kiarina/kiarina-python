from kiarina.agi.base.token_utils import ImageSize, calc_pdf_token


def test_calc_pdf_token() -> None:
    token_count = calc_pdf_token("Hello", [ImageSize(width=100, height=100)])
    assert token_count > 0
    print(f"Token count: {token_count}")
