import pytest

from kiarina.i18n._utils.normalize_language_tag import normalize_language_tag


@pytest.mark.parametrize(
    ("language", "expected"),
    [
        ("ja", "ja"),
        ("EN_us", "en-US"),
        ("en_US.UTF-8", "en-US"),
        ("zh_hant_tw", "zh-Hant-TW"),
        ("es_419", "es-419"),
        ("C", "en"),
        ("POSIX", "en"),
        ("fr:en", "fr"),
    ],
)
def test_normalize_language_tag(language: str, expected: str) -> None:
    assert normalize_language_tag(language) == expected


@pytest.mark.parametrize(
    "language",
    [
        "",
        "messages",
        "catalog",
    ],
)
def test_normalize_language_tag_invalid(language: str) -> None:
    with pytest.raises(ValueError):
        normalize_language_tag(language)
