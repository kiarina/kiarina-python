from .._settings import settings_manager


def get_default_encoding() -> str:
    return settings_manager.settings.default_encoding
