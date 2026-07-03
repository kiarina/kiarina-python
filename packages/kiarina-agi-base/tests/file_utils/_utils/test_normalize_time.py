from kiarina.agi.base.file_utils import normalize_time


def test_normalize_time() -> None:
    assert normalize_time(5.0, 10.0) == 5.0
    assert normalize_time(-1.0, 10.0) == 10.0
    assert normalize_time(-2.0, 10.0) == 9.0
    assert normalize_time(-11.0, 10.0) == 0.0
    assert normalize_time(11.0, 10.0) == 10.0
