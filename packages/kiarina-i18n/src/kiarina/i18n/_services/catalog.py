import yaml

from .._types.i18n_key import I18nKey
from .._types.i18n_scope import I18nScope
from .._types.language import Language


class Catalog:
    """Service for managing translation catalog.

    This class provides methods to add catalog data from dictionaries or YAML files,
    and retrieve translation text for a given language, scope, and key.

    Example:
        >>> from kiarina.i18n import catalog
        >>>
        >>> # Add from dict
        >>> catalog.add_from_dict({
        ...     "en": {"app": {"title": "My App"}},
        ...     "ja": {"app": {"title": "マイアプリ"}},
        ... })
        >>>
        >>> # Add from file
        >>> catalog.add_from_file("translations.yaml")
        >>>
        >>> # Get text
        >>> catalog.get_text("ja", "app", "title")
        'マイアプリ'
        >>>
        >>> # Clear all
        >>> catalog.clear()
    """

    def __init__(self) -> None:
        self._data: dict[Language, dict[I18nScope, dict[I18nKey, str]]] = {}

    def add_from_dict(
        self,
        data: dict[Language, dict[I18nScope, dict[I18nKey, str]]],
    ) -> None:
        """Add catalog data from dictionary (deep merge).

        Args:
            data: Catalog data to add.

        Example:
            >>> catalog.add_from_dict({
            ...     "en": {"app": {"title": "My App"}},
            ...     "ja": {"app": {"title": "マイアプリ"}},
            ... })
        """
        self._data = self._deep_merge(self._data, data)

    def add_from_file(self, file_path: str) -> None:
        """Add catalog data from YAML file (deep merge).

        Args:
            file_path: Path to YAML file containing catalog data.

        Example:
            >>> catalog.add_from_file("translations.yaml")
        """
        with open(file_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
            self.add_from_dict(data)

    def clear(self) -> None:
        """Clear all catalog data.

        Example:
            >>> catalog.clear()
        """
        self._data = {}

    def get_text(
        self,
        language: Language,
        scope: I18nScope,
        key: I18nKey,
    ) -> str | None:
        """Get translation text from catalog.

        Args:
            language: Target language.
            scope: Translation scope.
            key: Translation key.

        Returns:
            Translation text if found, None otherwise.

        Example:
            >>> catalog.get_text("ja", "app", "title")
            'マイアプリ'
        """
        return self._data.get(language, {}).get(scope, {}).get(key)

    def _deep_merge(
        self,
        base: dict[Language, dict[I18nScope, dict[I18nKey, str]]],
        update: dict[Language, dict[I18nScope, dict[I18nKey, str]]],
    ) -> dict[Language, dict[I18nScope, dict[I18nKey, str]]]:
        """Deep merge two catalog dictionaries.

        Args:
            base: Base dictionary.
            update: Dictionary to merge into base.

        Returns:
            Merged dictionary.
        """
        result = base.copy()

        for language, scopes in update.items():
            if language not in result:
                result[language] = {}

            for scope, keys in scopes.items():
                if scope not in result[language]:
                    result[language][scope] = {}

                result[language][scope].update(keys)

        return result


# Module-level singleton instance
catalog = Catalog()
