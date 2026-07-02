# kiarina-i18n

[![PyPI version](https://badge.fury.io/py/kiarina-i18n.svg)](https://badge.fury.io/py/kiarina-i18n)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-i18n.svg)](https://pypi.org/project/kiarina-i18n/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[English](README.md) | 日本語

> [!NOTE] これは何？
> dictionary や YAML の翻訳 catalog を、関数または型付き Pydantic model から利用するパッケージ。

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
  language、scope、key で catalog の text を取得し、template 変数を展開できます。
- **Loading Catalogs**
  dictionary、file system、package resource の YAML から catalog を構成できます。
- **Defining Typed Translations**
  Pydantic model の field として翻訳 key と既定 text を定義できます。
- **Translating Pydantic Schemas**
  Pydantic model の docstring と field description を言語別に変換できます。

### Translating Text

catalog は `language → scope → key → text` の順に構成します。

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

翻訳は指定 language の詳細な tag から親 tag、続いて default language の順に検索します。たとえば `ja-JP` では `ja-JP`、`ja`、`en` の順です。

該当する翻訳がない場合は `default`、それもなければ `<scope>#<key>` を返します。`$name` 形式の template 変数には `string.Template.safe_substitute` を使用するため、値が渡されていない変数はそのまま残ります。

### Loading Catalogs

複数回追加した catalog は深く merge され、同じ language、scope、key の値は後から追加した値で置き換わります。

```python
from kiarina.i18n import catalog

catalog.add_from_file("translations.yaml")
catalog.add_from_dir("translations")
catalog.add_from_package_file("my_app.catalogs", "ja.yaml")
catalog.add_from_package_dir("my_app.catalogs")
```

`add_from_dir` は子 directory も検索します。`add_from_package_dir` は指定 package の直下だけを検索します。

YAML file name が `ja.yaml` や `en-US.yaml` のような language tag の場合、file の内容をその language の catalog として扱えます。

```yaml
app.greeting:
  hello: "こんにちは、$name!"
```

それ以外の file nameでは、top level に language を記述します。

```yaml
en:
  app.greeting:
    hello: "Hello, $name!"
ja:
  app.greeting:
    hello: "こんにちは、$name!"
```

### Defining Typed Translations

`I18n` の subclass では、field name が key、default value が翻訳の fallback になります。

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

`scope` を省略すると `<module>.<class name>` を使用します。`get_i18n` の `language` を省略すると system language を使用します。

通常の Pydantic model も `get_i18n` に渡せます。この場合、最初の private module より前の public module path を scope として使用します。

### Translating Pydantic Schemas

`translate_pydantic_model` は元の model を変更せず、翻訳した model class を新しく作成します。`__doc__` key で model の docstring、各 field name の key で field description を翻訳します。

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

`list[I18nSubclass]` と `dict[str, I18nSubclass]` の field annotation は、内側の model も再帰的に変換します。

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

`get_i18n` は model の各 field を翻訳した instance を返します。`language` を省略した場合は `get_system_language` の結果を使用します。

`get_system_language` は `LANG`、`LC_ALL`、`LC_MESSAGES`、`LANGUAGE` の順に環境変数を確認し、次に `locale.getlocale()` を使用します。検出できない場合と `C` / `POSIX` locale の場合は `en` を返します。

`get_translator` は共有 `catalog` と `settings_manager.settings.default_language` を使用して `Translator` を作成します。

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

`language` と `default_language` は初期化時に正規化されます。無効な language tag を指定すると `ValueError` を送出します。

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

`add_from_file` と `add_from_dir` は file system の YAML を読みます。`add_from_package_file` と `add_from_package_dir` は import 可能な package resource を読みます。

directory が存在しない場合は `NotADirectoryError`、対象の YAML や package が見つからない場合は `FileNotFoundError` を送出します。`get_text` は language tag が無効な場合を含め、該当する text がなければ `None` を返します。

#### `I18n`

```python
class I18n(BaseModel):
    def __init_subclass__(
        cls,
        scope: I18nScope = "",
        **kwargs: Any,
    ) -> None: ...
```

subclass は frozen Pydantic model になり、未定義 field の入力を拒否します。翻訳対象の field は subclass で定義します。

#### Settings

```python
class I18nSettings(BaseSettings):
    default_language: Language = "en"

settings_manager: SettingsManager[I18nSettings]
```

`default_language` は翻訳が見つからない場合に使用する language です。`settings_manager` は `pydantic-settings-manager` による共有設定 manager です。

#### Catalog instance

```python
catalog: Catalog
```

package 内で共有する catalog instance です。test 間などで状態を破棄する場合は `catalog.clear()` を呼びます。

#### Types

```python
Language: TypeAlias = str
I18nScope: TypeAlias = str
I18nKey: TypeAlias = str
```

`Language` は BCP 47 language tag、`I18nScope` は key の namespace、`I18nKey` は scope 内の翻訳 key を表します。

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

元の Pydantic model の config、base class、module、field attributes を維持しながら、docstring と field description を翻訳した新しい model class を返します。
