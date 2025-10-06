from kiarina.lib.google.auth import hello


def test_hello():
    assert hello() == "Hello, world!"
