from kiarina.i18n import clear_cache, get_catalog, get_translator, settings_manager


def test_clear_cache_clears_get_catalog():
    """Test that clear_cache clears get_catalog cache."""
    # Setup catalog
    settings_manager.user_config = {
        "catalog": {
            "en": {"app": {"title": "Title"}},
        }
    }

    # Call get_catalog to populate cache
    catalog1 = get_catalog()
    assert catalog1["en"]["app"]["title"] == "Title"

    # Modify settings
    settings_manager.user_config = {
        "catalog": {
            "en": {"app": {"title": "New Title"}},
        }
    }

    # Without clear_cache, should return cached value
    catalog2 = get_catalog()
    assert catalog2 is catalog1  # Same object (cached)

    # Clear cache
    clear_cache()

    # Should return new value
    catalog3 = get_catalog()
    assert catalog3 is not catalog1  # Different object
    assert catalog3["en"]["app"]["title"] == "New Title"


def test_clear_cache_clears_get_translator():
    """Test that clear_cache clears get_translator cache."""
    # Setup catalog
    settings_manager.user_config = {
        "catalog": {
            "en": {"app": {"title": "Title"}},
        }
    }

    # Call get_translator to populate cache
    t1 = get_translator("en", "app")
    assert t1("title") == "Title"

    # Modify settings
    settings_manager.user_config = {
        "catalog": {
            "en": {"app": {"title": "New Title"}},
        }
    }

    # Without clear_cache, should return cached translator
    t2 = get_translator("en", "app")
    assert t2 is t1  # Same object (cached)
    assert t2("title") == "Title"  # Old value

    # Clear cache
    clear_cache()

    # Should return new translator
    t3 = get_translator("en", "app")
    assert t3 is not t1  # Different object
    assert t3("title") == "New Title"


def test_clear_cache_multiple_calls():
    """Test that clear_cache can be called multiple times safely."""
    settings_manager.user_config = {
        "catalog": {
            "en": {"app": {"title": "Title"}},
        }
    }

    # Populate caches
    get_catalog()
    get_translator("en", "app")

    # Clear multiple times (should not raise errors)
    clear_cache()
    clear_cache()
    clear_cache()

    # Should still work
    catalog = get_catalog()
    assert catalog["en"]["app"]["title"] == "Title"


def test_clear_cache_with_empty_caches():
    """Test that clear_cache works even when caches are empty."""
    # Clear without populating caches (should not raise errors)
    clear_cache()

    # Should still work
    settings_manager.user_config = {
        "catalog": {
            "en": {"app": {"title": "Title"}},
        }
    }
    catalog = get_catalog()
    assert catalog["en"]["app"]["title"] == "Title"
