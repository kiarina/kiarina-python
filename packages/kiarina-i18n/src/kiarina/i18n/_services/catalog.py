from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import TypeAlias, cast

import yaml

from .._types.i18n_key import I18nKey
from .._types.i18n_scope import I18nScope
from .._types.language import Language
from .._utils.normalize_language_tag import normalize_language_tag

_CatalogData: TypeAlias = dict[Language, dict[I18nScope, dict[I18nKey, str]]]
_LanguageCatalogData: TypeAlias = dict[I18nScope, dict[I18nKey, str]]


class Catalog:
    def __init__(self) -> None:
        self._data: dict[Language, dict[I18nScope, dict[I18nKey, str]]] = {}

    def add_from_dict(
        self,
        data: dict[Language, dict[I18nScope, dict[I18nKey, str]]],
    ) -> None:
        self._data = self._deep_merge(self._data, self._normalize_data(data))

    def add_from_file(self, file_path: str) -> None:
        with open(file_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

            if data is not None:
                self.add_from_dict(
                    self._normalize_file_data(data, Path(file_path).stem)
                )

    def add_from_dir(self, dir_path: str) -> None:
        dir_path_obj = Path(dir_path)

        if not dir_path_obj.is_dir():
            raise NotADirectoryError(f"Not a directory: {dir_path}")

        yaml_files = sorted(dir_path_obj.rglob("*.yaml")) + sorted(
            dir_path_obj.rglob("*.yml")
        )

        if not yaml_files:
            raise FileNotFoundError(f"No YAML files found in directory: {dir_path}")

        for yaml_file in yaml_files:
            self.add_from_file(str(yaml_file))

    def add_from_package_file(self, package: str, file_path: str) -> None:
        try:
            resource_files = files(package)
            resource_file = resource_files.joinpath(file_path)

            if not resource_file.is_file():
                raise FileNotFoundError(
                    f"Package resource not found: {package}/{file_path}"
                )

            content = resource_file.read_text(encoding="utf-8")
            data = yaml.safe_load(content)

            if data is not None:
                self.add_from_dict(
                    self._normalize_file_data(data, Path(file_path).stem)
                )

        except ModuleNotFoundError as e:
            raise FileNotFoundError(
                f"Package not found: '{package}' does not exist"
            ) from e

    def add_from_package_dir(self, package: str) -> None:
        try:
            resource_dir = files(package)

            yaml_files: list[Traversable] = []

            try:
                for item in resource_dir.iterdir():
                    if item.is_file() and item.name.endswith((".yaml", ".yml")):
                        yaml_files.append(item)

            except (FileNotFoundError, OSError) as e:
                raise FileNotFoundError(
                    f"Package directory not accessible: {package}"
                ) from e

            if not yaml_files:
                raise FileNotFoundError(f"No YAML files found in package: {package}")

            yaml_files.sort(key=lambda p: str(p))

            for yaml_file in yaml_files:
                content = yaml_file.read_text(encoding="utf-8")
                data = yaml.safe_load(content)

                if data is not None:
                    self.add_from_dict(
                        self._normalize_file_data(data, Path(yaml_file.name).stem)
                    )

        except ModuleNotFoundError as e:
            raise FileNotFoundError(
                f"Package not found: '{package}' does not exist"
            ) from e

    def clear(self) -> None:
        self._data = {}

    def get_text(
        self,
        language: Language,
        scope: I18nScope,
        key: I18nKey,
    ) -> str | None:
        try:
            normalized_language = normalize_language_tag(language)
        except ValueError:
            return None

        return self._data.get(normalized_language, {}).get(scope, {}).get(key)

    def _deep_merge(
        self,
        base: _CatalogData,
        update: _CatalogData,
    ) -> _CatalogData:
        result = base.copy()

        for language, scopes in update.items():
            if language not in result:
                result[language] = {}

            for scope, keys in scopes.items():
                if scope not in result[language]:
                    result[language][scope] = {}

                result[language][scope].update(keys)

        return result

    def _normalize_data(self, data: _CatalogData) -> _CatalogData:
        normalized_data: _CatalogData = {}

        for language, scopes in data.items():
            normalized_language = normalize_language_tag(language)

            if normalized_language not in normalized_data:
                normalized_data[normalized_language] = {}

            for scope, keys in scopes.items():
                if scope not in normalized_data[normalized_language]:
                    normalized_data[normalized_language][scope] = {}

                normalized_data[normalized_language][scope].update(keys)

        return normalized_data

    def _normalize_file_data(
        self,
        data: object,
        file_stem: str,
    ) -> _CatalogData:
        catalog_data = cast(_CatalogData, data)

        if not _is_language_tag(file_stem):
            return catalog_data

        normalized_file_stem = normalize_language_tag(file_stem)

        for language in catalog_data:
            try:
                if normalize_language_tag(language) == normalized_file_stem:
                    return catalog_data
            except ValueError:
                continue

        return {normalized_file_stem: cast(_LanguageCatalogData, data)}


def _is_language_tag(language: str) -> bool:
    if any(separator in language for separator in ("_", ".", ":", "@")):
        return False

    try:
        normalize_language_tag(language)
    except ValueError:
        return False

    return True
