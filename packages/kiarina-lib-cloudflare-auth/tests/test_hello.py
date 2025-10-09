from kiarina.lib.cloudflare.auth import hello


def test_hello():
    assert hello() == "Hello, world!"
