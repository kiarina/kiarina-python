from kiarina.agi.base.token_utils import ImageSize, calc_image_token


def test_calc_image_token() -> None:
    assert calc_image_token(ImageSize(1024, 1024)) == 630
    assert calc_image_token(ImageSize(2048, 4096)) == 910
    assert calc_image_token(ImageSize(512, 512)) == 210
