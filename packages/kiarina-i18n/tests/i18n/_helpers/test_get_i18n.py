from typing import Any

from pydantic import BaseModel

from kiarina.i18n import I18n, catalog, get_i18n


def test_get_i18n_with_default_values() -> None:
    """Test get_i18n returns default values when no translation exists."""

    class MyI18n(I18n, scope="test.default"):
        title: str = "Default Title"
        description: str = "Default Description"

    # No catalog configured, should return default values
    catalog.add_from_dict({})

    t = get_i18n(MyI18n, "en")
    assert t._scope == "test.default"
    assert t.title == "Default Title"
    assert t.description == "Default Description"


def test_get_i18n_with_translations() -> None:
    """Test get_i18n returns translated values."""

    class MyI18n(I18n, scope="test.translated"):
        title: str = "Default Title"
        description: str = "Default Description"

    # Configure catalog with translations
    catalog.add_from_dict(
        {
            "ja": {
                "test.translated": {
                    "title": "日本語タイトル",
                    "description": "日本語説明",
                }
            },
            "en": {
                "test.translated": {
                    "title": "English Title",
                    "description": "English Description",
                }
            },
        }
    )

    # Get Japanese translation
    t_ja = get_i18n(MyI18n, "ja")
    assert t_ja._scope == "test.translated"
    assert t_ja.title == "日本語タイトル"
    assert t_ja.description == "日本語説明"

    # Get English translation
    t_en = get_i18n(MyI18n, "en")
    assert t_en._scope == "test.translated"
    assert t_en.title == "English Title"
    assert t_en.description == "English Description"


def test_get_i18n_uses_system_language_by_default(monkeypatch: Any) -> None:
    """Test get_i18n uses system language when language is omitted."""

    class MyI18n(I18n, scope="test.system_language"):
        title: str = "Default Title"

    monkeypatch.setenv("LANG", "ja_JP.UTF-8")
    catalog.add_from_dict(
        {
            "ja": {
                "test.system_language": {
                    "title": "システム言語",
                }
            }
        }
    )

    t = get_i18n(MyI18n)

    assert t.title == "システム言語"


def test_get_i18n_uses_system_language_when_language_is_none(monkeypatch: Any) -> None:
    """Test get_i18n uses system language when language is None."""

    class MyI18n(I18n, scope="test.none_language"):
        title: str = "Default Title"

    monkeypatch.setenv("LANG", "ja_JP.UTF-8")
    catalog.add_from_dict(
        {
            "ja": {
                "test.none_language": {
                    "title": "Noneの言語",
                }
            }
        }
    )

    t = get_i18n(MyI18n, None)

    assert t.title == "Noneの言語"


def test_get_i18n_with_partial_translations() -> None:
    """Test get_i18n falls back to default for missing translations."""

    class MyI18n(I18n, scope="test.partial"):
        title: str = "Default Title"
        description: str = "Default Description"
        error: str = "Default Error"

    # Configure catalog with partial translations
    catalog.add_from_dict(
        {
            "ja": {
                "test.partial": {
                    "title": "日本語タイトル",
                    # description is missing
                }
            }
        }
    )

    t = get_i18n(MyI18n, "ja")
    assert t.title == "日本語タイトル"
    assert t.description == "Default Description"  # Fallback to default
    assert t.error == "Default Error"  # Fallback to default


def test_get_i18n_with_default_language() -> None:
    """Test get_i18n uses default language."""

    class MyI18n(I18n, scope="test.fallback"):
        title: str = "Default Title"

    # Configure catalog with default language
    from kiarina.i18n import settings_manager

    settings_manager.user_config = {
        "default_language": "en",
    }
    catalog.add_from_dict(
        {
            "en": {
                "test.fallback": {
                    "title": "English Title",
                }
            }
        }
    )

    # Request non-existent language, should fallback to English
    t = get_i18n(MyI18n, "fr")
    assert t.title == "English Title"


def test_get_i18n_type_safety() -> None:
    """Test that get_i18n preserves type information."""

    class MyI18n(I18n, scope="test.type"):
        title: str = "Title"
        count: int = 42

    catalog.add_from_dict({})

    t = get_i18n(MyI18n, "en")

    # Type checker should recognize these fields
    assert isinstance(t.title, str)
    assert isinstance(t.count, int)


def test_get_i18n_multiple_instances() -> None:
    """Test that multiple i18n classes can coexist."""

    class ModuleAI18n(I18n, scope="module.a"):
        title: str = "Module A"

    class ModuleBI18n(I18n, scope="module.b"):
        title: str = "Module B"

    catalog.add_from_dict(
        {
            "ja": {
                "module.a": {"title": "モジュールA"},
                "module.b": {"title": "モジュールB"},
            }
        }
    )

    t_a = get_i18n(ModuleAI18n, "ja")
    t_b = get_i18n(ModuleBI18n, "ja")

    assert t_a.title == "モジュールA"
    assert t_b.title == "モジュールB"


def test_get_i18n_with_scope_field() -> None:
    """Test that 'scope' can be used as a regular translation key."""

    class MyI18n(I18n, scope="test.scope_field"):
        scope: str = "Default Scope Text"
        title: str = "Default Title"

    catalog.add_from_dict(
        {
            "ja": {
                "test.scope_field": {
                    "scope": "スコープテキスト",
                    "title": "タイトル",
                }
            }
        }
    )

    t = get_i18n(MyI18n, "ja")

    # _scope should be the class-level scope
    assert t._scope == "test.scope_field"
    # scope field should be translated
    assert t.scope == "スコープテキスト"
    assert t.title == "タイトル"


def test_get_i18n_with_base_model_uses_module_as_scope() -> None:
    """Test get_i18n supports regular Pydantic models."""

    class MyModel(BaseModel):
        title: str = "Default Title"

    MyModel.__module__ = "test.public_model"

    catalog.add_from_dict(
        {
            "ja": {
                "test.public_model": {
                    "title": "公開モデル",
                }
            }
        }
    )

    t = get_i18n(MyModel, "ja")

    assert t.title == "公開モデル"


def test_get_i18n_with_base_model_uses_public_module_before_private_word() -> None:
    """Test BaseModel scope removes private module words and everything after them."""

    class MyModel(BaseModel):
        title: str = "Default Title"

    MyModel.__module__ = "hoge.fuga._fire.aaa"

    catalog.add_from_dict(
        {
            "ja": {
                "hoge.fuga": {
                    "title": "公開スコープ",
                },
                "hoge.fuga._fire.aaa": {
                    "title": "内部スコープ",
                },
            }
        }
    )

    t = get_i18n(MyModel, "ja")

    assert t.title == "公開スコープ"
