from kiarina.lib.google.cloud_storage import hello


def test_hello():
    assert hello() == "Hello, world!"
