from kiarina.lib.atlassian import AtlassianSettings


def test_atlassian_settings():
    settings = AtlassianSettings()
    assert settings.url == ""
    assert settings.username == ""
    assert settings.password.get_secret_value() == ""
