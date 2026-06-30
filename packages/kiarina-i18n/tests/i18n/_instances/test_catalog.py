def test_catalog_singleton_behavior() -> None:
    """Test that catalog behaves as a singleton at module level."""
    from kiarina.i18n import catalog as catalog1, catalog as catalog2

    assert catalog1 is catalog2

    catalog1.clear()
    catalog1.add_from_dict(
        {
            "en": {"test": {"key": "value"}},
        }
    )

    assert catalog2.get_text("en", "test", "key") == "value"

    catalog1.clear()
