import logging
from string import Template
from typing import Any

from .._services.catalog import Catalog
from .._types.i18n_key import I18nKey
from .._types.i18n_scope import I18nScope
from .._types.language import Language
from .._utils.normalize_language_tag import normalize_language_tag

logger = logging.getLogger(__name__)


class Translator:
    def __init__(
        self,
        *,
        catalog: Catalog,
        language: Language,
        scope: I18nScope,
        default_language: Language = "en",
    ) -> None:
        self.catalog = catalog
        self.language = normalize_language_tag(language)
        self.scope = scope
        self.default_language = normalize_language_tag(default_language)

    def __call__(self, key: I18nKey, default: str | None = None, **kwargs: Any) -> str:
        text = None

        for language in _get_language_fallbacks(self.language, self.default_language):
            text = self.catalog.get_text(language, self.scope, key)

            if text is not None:
                break

        if text is None:
            text = default

        if text is None:
            logger.error(
                f"Translation not found for key '{key}' in scope '{self.scope}' "
                f"and language '{self.language}'"
            )

            text = f"{self.scope}#{key}"

        if kwargs:
            return Template(text).safe_substitute(**kwargs)

        return text


def _get_language_fallbacks(
    language: Language,
    default_language: Language = "en",
) -> list[Language]:
    languages: list[Language] = []

    for candidate in (
        *_get_language_parents(language),
        *_get_language_parents(default_language),
    ):
        if candidate not in languages:
            languages.append(candidate)

    return languages


def _get_language_parents(language: Language) -> list[Language]:
    language_tag = normalize_language_tag(language)
    parts = language_tag.split("-")
    return ["-".join(parts[:index]) for index in range(len(parts), 0, -1)]
