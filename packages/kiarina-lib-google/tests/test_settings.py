from kiarina.lib.google import GoogleSettings


def test_scopes_default_to_empty():
    assert GoogleSettings().scopes == []
