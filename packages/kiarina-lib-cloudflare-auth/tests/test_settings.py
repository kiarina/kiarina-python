from pydantic import SecretStr
from kiarina.lib.cloudflare.auth import CloudflareAuthSettings, settings_manager


def test_settings():
    settings_manager.user_config = {
        "default": CloudflareAuthSettings(
            account_id="test",
            api_token=SecretStr("testtoken"),
        ).model_dump()
    }
    settings = settings_manager.settings
    assert settings.account_id == "test"
    assert settings.api_token.get_secret_value() == "testtoken"
