from kiarina.agi.base.file_utils import normalize_page


def test_normalize_page() -> None:
    assert normalize_page(1, 10) == 1
    assert normalize_page(5, 10) == 5
    assert normalize_page(10, 10) == 10
    assert normalize_page(11, 10) == 10
    assert normalize_page(-1, 10) == 10
    assert normalize_page(-2, 10) == 9
    assert normalize_page(-10, 10) == 1
    assert normalize_page(-11, 10) == 1
