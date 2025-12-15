from functools import lru_cache

import yaml

from .._settings import settings_manager
from .._types.catalog import Catalog


@lru_cache(maxsize=None)
def get_catalog() -> Catalog:
    """
    Get the translation catalog from settings.

    This function is cached to avoid loading the catalog multiple times.
    The cache is cleared when settings are updated.

    Returns:
        Translation catalog loaded from file or settings.

    Example:
        ```python
        from kiarina.i18n import get_catalog, settings_manager

        # Configure catalog
        settings_manager.user_config = {
            "catalog": {
                "en": {"app.greeting": {"hello": "Hello!"}},
                "ja": {"app.greeting": {"hello": "こんにちは!"}}
            }
        }

        # Get catalog
        catalog = get_catalog()
        print(catalog["en"]["app.greeting"]["hello"])  # "Hello!"
        ```
    """
    settings = settings_manager.settings

    if settings.catalog_file is not None:
        with open(settings.catalog_file, encoding="utf-8") as f:
            catalog: Catalog = yaml.safe_load(f)
            return catalog
    else:
        return settings.catalog
