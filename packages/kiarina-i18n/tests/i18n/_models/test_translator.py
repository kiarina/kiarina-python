from typing import TypeAlias

from kiarina.i18n import Translator, catalog

CatalogData: TypeAlias = dict[str, dict[str, dict[str, str]]]


def test_translator_basic(sample_catalog: CatalogData) -> None:
    """Test basic translation."""
    catalog.add_from_dict(sample_catalog)
    t = Translator(catalog=catalog, language="en", scope="app.greeting")
    assert t("hello", name="World") == "Hello, World!"
    assert t("goodbye") == "Goodbye!"


def test_translator_japanese(sample_catalog: CatalogData) -> None:
    """Test Japanese translation."""
    catalog.add_from_dict(sample_catalog)
    t = Translator(catalog=catalog, language="ja", scope="app.greeting")
    assert t("hello", name="世界") == "こんにちは、世界!"
    assert t("goodbye") == "さようなら!"


def test_translator_fallback(sample_catalog: CatalogData) -> None:
    """Test fallback to English when translation is not found."""
    # Remove Japanese translation for "goodbye"
    del sample_catalog["ja"]["app.greeting"]["goodbye"]

    catalog.add_from_dict(sample_catalog)
    t = Translator(
        catalog=catalog,
        language="ja",
        scope="app.greeting",
        default_language="en",
    )
    assert t("goodbye") == "Goodbye!"


def test_translator_fallbacks_from_region_to_language() -> None:
    """Test fallback from BCP 47 region tag to base language."""
    catalog.add_from_dict(
        {
            "pt": {
                "app.greeting": {
                    "hello": "Olá, $name!",
                },
            },
            "en": {
                "app.greeting": {
                    "hello": "Hello, $name!",
                },
            },
        }
    )

    t = Translator(catalog=catalog, language="pt-BR", scope="app.greeting")

    assert t("hello", name="World") == "Olá, World!"


def test_translator_fallbacks_from_script_region_to_script_then_language() -> None:
    """Test fallback from BCP 47 script-region tag to script tag."""
    catalog.add_from_dict(
        {
            "zh-Hant": {
                "app.greeting": {
                    "hello": "你好",
                },
            },
            "zh": {
                "app.greeting": {
                    "goodbye": "再見",
                },
            },
            "en": {
                "app.greeting": {
                    "hello": "Hello",
                    "goodbye": "Goodbye",
                },
            },
        }
    )

    t = Translator(catalog=catalog, language="zh-Hant-TW", scope="app.greeting")

    assert t("hello") == "你好"
    assert t("goodbye") == "再見"


def test_translator_uses_default_language_fallback_chain() -> None:
    """Test default language also falls back through parent tags."""
    catalog.add_from_dict(
        {
            "en": {
                "app.greeting": {
                    "hello": "Hello",
                },
            },
        }
    )

    t = Translator(
        catalog=catalog,
        language="fr-CA",
        scope="app.greeting",
        default_language="en-US",
    )

    assert t("hello") == "Hello"


def test_translator_default(sample_catalog: CatalogData) -> None:
    """Test default value when translation is not found."""
    catalog.add_from_dict(sample_catalog)
    t = Translator(catalog=catalog, language="en", scope="app.greeting")
    assert t("unknown", default="Default text") == "Default text"


def test_translator_missing_key(sample_catalog: CatalogData) -> None:
    """Test behavior when key is missing and no default is provided."""
    catalog.add_from_dict(sample_catalog)
    t = Translator(catalog=catalog, language="en", scope="app.greeting")
    result = t("unknown")
    assert result == "app.greeting#unknown"


def test_translator_template_substitution(sample_catalog: CatalogData) -> None:
    """Test template variable substitution."""
    catalog.add_from_dict(sample_catalog)
    t = Translator(catalog=catalog, language="en", scope="app.greeting")
    assert t("hello", name="Alice") == "Hello, Alice!"
    assert t("hello", name="Bob") == "Hello, Bob!"


def test_translator_different_scope(sample_catalog: CatalogData) -> None:
    """Test translation with different scope."""
    catalog.add_from_dict(sample_catalog)
    t = Translator(catalog=catalog, language="en", scope="app.error")
    assert t("not_found") == "Not found"

    t_ja = Translator(catalog=catalog, language="ja", scope="app.error")
    assert t_ja("not_found") == "見つかりません"
