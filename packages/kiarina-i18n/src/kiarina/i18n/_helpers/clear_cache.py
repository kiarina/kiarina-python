from .get_catalog import get_catalog
from .get_translator import get_translator


def clear_cache() -> None:
    """
    Clear all i18n-related caches.

    This function clears:
    - Translation catalog cache (get_catalog)
    - Translator instance cache (get_translator)

    Useful when you need to reload configuration or reset state during testing.

    Example:
        ```python
        from kiarina.i18n import clear_cache, settings_manager

        # Change settings
        settings_manager.user_config = {"catalog": {...}}

        # Clear caches to apply new settings
        clear_cache()
        ```
    """
    get_catalog.cache_clear()
    get_translator.cache_clear()
