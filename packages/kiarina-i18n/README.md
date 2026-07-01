# kiarina-i18n

English | [日本語](README.ja.md)

[![PyPI version](https://badge.fury.io/py/kiarina-i18n.svg)](https://badge.fury.io/py/kiarina-i18n)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-i18n.svg)](https://pypi.org/project/kiarina-i18n/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> [!NOTE] What is this?
> A package for using translation catalogs from dictionaries or YAML through functions or typed Pydantic models.

## Dependencies

| Package | Version | License |
| --- | --- | --- |
| [Pydantic](https://github.com/pydantic/pydantic) | `>=2.0.0` | [MIT](https://github.com/pydantic/pydantic/blob/main/LICENSE) |
| [pydantic-settings](https://github.com/pydantic/pydantic-settings) | `>=2.0.0` | [MIT](https://github.com/pydantic/pydantic-settings/blob/main/LICENSE) |
| [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) | `>=3.2.0` | [MIT](https://github.com/kiarina/pydantic-settings-manager/blob/main/LICENSE) |
| [PyYAML](https://github.com/yaml/pyyaml) | `>=6.0.0` | [MIT](https://github.com/yaml/pyyaml/blob/main/LICENSE) |

## Installation

```bash
pip install kiarina-i18n
```

## Features

- **Translating Text**
  Retrieve catalog text by language, scope, and key, then substitute template variables.
- **Loading Catalogs**
  Build catalogs from dictionaries, file-system YAML, and package-resource YAML.
- **Defining Typed Translations**
  Define translation keys and default text as fields on a Pydantic model.
- **Translating Pydantic Schemas**
  Translate Pydantic model docstrings and field descriptions by language.

### Translating Text

Catalog data is structured as `language → scope → key → text`.

```python
from kiarina.i18n import catalog, get_translator

catalog.add_from_dict(
    {
        "en": {"app.greeting": {"hello": "Hello, $name!"}},
        "ja": {"app.greeting": {"hello": "こんにちは、$name!"}},
    }
)

translate = get_translator("ja", "app.greeting")
message = translate("hello", name="World")
```

Translations are searched from the most specific requested language tag through its parent tags, followed by the default language. For example, `ja-JP` searches `ja-JP`, `ja`, then `en`.

If no translation exists, the translator returns `default`, or `<scope>#<key>` when no default is given. Template variables use `string.Template.safe_substitute`, so variables without supplied values remain unchanged.

### Loading Catalogs

Catalog additions are deeply merged. A later value replaces an earlier value with the same language, scope, and key.

```python
from kiarina.i18n import catalog

catalog.add_from_file("translations.yaml")
catalog.add_from_dir("translations")
catalog.add_from_package_file("my_app.catalogs", "ja.yaml")
catalog.add_from_package_dir("my_app.catalogs")
```

`add_from_dir` searches child directories. `add_from_package_dir` searches only the specified package's immediate directory.

When a YAML file is named after a language tag, such as `ja.yaml` or `en-US.yaml`, its contents are treated as the catalog for that language.

```yaml
app.greeting:
  hello: "こんにちは、$name!"
```

For other file names, declare languages at the top level.

```yaml
en:
  app.greeting:
    hello: "Hello, $name!"
ja:
  app.greeting:
    hello: "こんにちは、$name!"
```

### Defining Typed Translations

In an `I18n` subclass, field names are keys and default values are translation fallbacks.

```python
from kiarina.i18n import I18n, catalog, get_i18n


class ProfileText(I18n, scope="app.profile"):
    title: str = "Profile"
    description: str = "Edit your profile."


catalog.add_from_dict(
    {
        "ja": {
            "app.profile": {
                "title": "プロフィール",
                "description": "プロフィールを編集します。",
            }
        }
    }
)

text = get_i18n(ProfileText, "ja")
```

If `scope` is omitted, `<module>.<class name>` is used. If `language` is omitted from `get_i18n`, the system language is used.

Regular Pydantic models can also be passed to `get_i18n`. Their scope is the public module path before the first private module segment.

### Translating Pydantic Schemas

`translate_pydantic_model` creates a translated model class without changing the original model. It translates the model docstring with the `__doc__` key and each field description with the corresponding field-name key.

```python
from pydantic import BaseModel, Field

from kiarina.i18n import catalog
from kiarina.i18n_pydantic import translate_pydantic_model


class UserInput(BaseModel):
    name: str = Field(description="Your name")


catalog.add_from_dict(
    {
        "ja": {
            "__main__": {
                "__doc__": "ユーザー入力",
                "name": "名前",
            }
        }
    }
)

JapaneseUserInput = translate_pydantic_model(UserInput, "ja")
```

Field annotations of `list[I18nSubclass]` and `dict[str, I18nSubclass]` recursively translate their inner models.

## API Reference

### `kiarina.i18n`

```python
from kiarina.i18n import (
    Catalog,
    I18n,
    I18nKey,
    I18nScope,
    I18nSettings,
    Language,
    Translator,
    catalog,
    get_i18n,
    get_system_language,
    get_translator,
    settings_manager,
)
```

#### Translation functions

```python
def get_i18n(
    model_class: type[T],
    language: Language | None = None,
) -> T: ...

def get_system_language() -> Language: ...

def get_translator(
    language: Language,
    scope: I18nScope,
) -> Translator: ...
```

`get_i18n` returns an instance with each model field translated. When `language` is omitted, it uses the result of `get_system_language`.

`get_system_language` checks the `LANG`, `LC_ALL`, `LC_MESSAGES`, and `LANGUAGE` environment variables in that order, followed by `locale.getlocale()`. It returns `en` when detection fails or the locale is `C` / `POSIX`.

`get_translator` creates a `Translator` using the shared `catalog` and `settings_manager.settings.default_language`.

#### `Translator`

```python
class Translator:
    def __init__(
        self,
        *,
        catalog: Catalog,
        language: Language,
        scope: I18nScope,
        default_language: Language = "en",
    ) -> None: ...

    def __call__(
        self,
        key: I18nKey,
        default: str | None = None,
        **kwargs: Any,
    ) -> str: ...
```

`language` and `default_language` are normalized during initialization. An invalid language tag raises `ValueError`.

#### `Catalog`

```python
class Catalog:
    def __init__(self) -> None: ...

    def add_from_dict(
        self,
        data: dict[
            Language,
            dict[I18nScope, dict[I18nKey, str]],
        ],
    ) -> None: ...

    def add_from_file(self, file_path: str) -> None: ...

    def add_from_dir(self, dir_path: str) -> None: ...

    def add_from_package_file(
        self,
        package: str,
        file_path: str,
    ) -> None: ...

    def add_from_package_dir(self, package: str) -> None: ...

    def clear(self) -> None: ...

    def get_text(
        self,
        language: Language,
        scope: I18nScope,
        key: I18nKey,
    ) -> str | None: ...
```

`add_from_file` and `add_from_dir` read file-system YAML. `add_from_package_file` and `add_from_package_dir` read resources from an importable package.

A missing directory raises `NotADirectoryError`. Missing YAML files or packages raise `FileNotFoundError`. `get_text` returns `None` when no text exists, including when the language tag is invalid.

#### `I18n`

```python
class I18n(BaseModel):
    def __init_subclass__(
        cls,
        scope: I18nScope = "",
        **kwargs: Any,
    ) -> None: ...
```

Subclasses are frozen Pydantic models and reject undefined fields. Define the fields to translate on each subclass.

#### Settings

```python
class I18nSettings(BaseSettings):
    default_language: Language = "en"

settings_manager: SettingsManager[I18nSettings]
```

`default_language` is used when a translation is unavailable. `settings_manager` is the shared configuration manager provided by `pydantic-settings-manager`.

#### Catalog instance

```python
catalog: Catalog
```

The package shares this catalog instance. Call `catalog.clear()` to discard state between tests or other isolated operations.

#### Types

```python
Language: TypeAlias = str
I18nScope: TypeAlias = str
I18nKey: TypeAlias = str
```

`Language` represents a BCP 47 language tag, `I18nScope` a namespace for keys, and `I18nKey` a translation key within a scope.

### `kiarina.i18n_pydantic`

```python
from kiarina.i18n_pydantic import translate_pydantic_model
```

#### `translate_pydantic_model`

```python
def translate_pydantic_model(
    model: type[T],
    language: str,
) -> type[T]: ...
```

Returns a new model class with translated docstrings and field descriptions while preserving the original Pydantic model's configuration, base class, module, and field attributes.
