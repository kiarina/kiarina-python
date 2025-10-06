from kiarina.lib.cloudflare import hello


def test_hello():
    assert hello() == "Hello, world!"
