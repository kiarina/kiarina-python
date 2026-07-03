from kiarina.agi.base.file_utils import is_uri


def test_is_uri() -> None:
    assert is_uri("http://example.com/file.txt")
    assert not is_uri("/path/to/local/file.txt")
