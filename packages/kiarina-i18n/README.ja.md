# kiarina-i18n

[English](README.md) | [日本語](README.ja.md)

Python applications 向けのシンプルな internationalization (i18n) utility です。

## Purpose

`kiarina-i18n` は、Python application に軽量で予測しやすい i18n の仕組みを提供します。複雑な文法規則や plural form は扱わず、単純な translation key、scope、fallback に集中しています。

plural form など高度な localization が必要な場合は、`gettext` などの既存ツールの利用を検討してください。

## Installation

```bash
pip install kiarina-i18n
```

## Quick Start

### Basic Usage (Functional API)

```python
from kiarina.i18n import catalog, get_translator

catalog.add_from_dict({
    "en": {"app.greeting": {"hello": "Hello, $name!"}},
    "ja": {"app.greeting": {"hello": "こんにちは、$name!"}},
})

t = get_translator("ja", "app.greeting")
print(t("hello", name="World"))
```

### Automatic Language Detection

`get_system_language()` は環境変数や locale からユーザーの system language を検出します。

```python
from kiarina.i18n import get_system_language

language = get_system_language()  # "ja-JP" や "en-US" などの BCP 47 tag
```

### Type-Safe Class-Based API (Recommended)

型安全性と IDE 補完を重視する場合は class-based API を推奨します。

```python
from pydantic import BaseModel
from kiarina.i18n import I18n, catalog, get_i18n


class AppI18n(I18n, scope="app.greeting"):
    hello: str = "Hello, $name!"
    goodbye: str = "Goodbye!"


class AppText(BaseModel):
    hello: str = "Hello, $name!"
    goodbye: str = "Goodbye!"


catalog.add_from_dict({
    "ja": {
        "app.greeting": {
            "hello": "こんにちは、$name!",
            "goodbye": "さようなら!",
        },
    },
})

t = get_i18n(AppI18n, "ja")
print(t.hello)

# language を省略すると system language が自動で使われます
system_t = get_i18n(AppI18n)
print(system_t.hello)
```

### Using Catalog Files

#### From File System

```python
from kiarina.i18n import catalog, get_translator

catalog.add_from_file("i18n_catalog.yaml")
catalog.add_from_dir("translations/")

t = get_translator("en", "app.greeting")
```

#### Language-Named Files

file name が `en.yaml`、`en-US.yaml`、`zh-Hant.yaml` のような BCP 47 language tag の場合、top-level の language key は省略できます。file content は file name から得た language の下に自動で登録されます。

例: `zh-Hant.yaml`

```yaml
app.greeting:
  hello: "你好，$name!"
  goodbye: "再見!"
```

#### From Package Resources

```python
from kiarina.i18n import catalog

catalog.add_from_package_file("myapp.i18n", "catalogs/en.yaml")
catalog.add_from_package_dir("myapp.i18n.catalogs")
```

### Pydantic Integration for LLM Tools

#### Basic Usage

`translate_pydantic_model` を使うと、LLM tool schema の description を runtime で言語別に変換できます。

```python
from pydantic import Field
from kiarina.i18n import I18n, catalog
from kiarina.i18n_pydantic import translate_pydantic_model


class ArgsSchema(I18n, scope="hoge_tool.args_schema"):
    """Hoge tool for processing data."""

    name: str = Field(description="Your Name")
    age: int = Field(description="Your Age")


catalog.add_from_dict({
    "ja": {
        "hoge_tool.args_schema": {
            "__doc__": "データ処理用のHogeツール。",
            "name": "あなたの名前",
            "age": "あなたの年齢",
        },
    },
})

translated_schema = translate_pydantic_model(ArgsSchema, "ja")
```

#### Nested I18n Models

`translate_pydantic_model` は、`list[I18n]` や `dict[str, I18n]` に含まれる nested I18n model の翻訳にも対応します。

## API Reference

### Class-Based API

#### `I18n`

翻訳 field を型付き class として宣言するための base class です。`scope="..."` を明示するか、module / class name から自動生成できます。

#### `get_i18n(model_class: type[T], language: str | None = None) -> T`

指定言語に翻訳された Pydantic model instance を返します。`language` を省略するか `None` を渡した場合は、`get_system_language()` の結果を自動で使います。`I18n` subclass は class-level scope を使い、通常の `BaseModel` は `__module__` を scope として使います。module path に `_schemas` など `_` prefix の word が含まれる場合は、その word 以降を除外した public module path を使います。

### Pydantic Model Translation (kiarina.i18n_pydantic)

#### `translate_pydantic_model(model: type[T], language: str) -> type[T]`

Pydantic model の class docstring と field description を catalog に基づいて翻訳した model class を返します。`I18n` subclass は class-level scope を使い、通常の `BaseModel` は `get_i18n()` と同じく public module path を scope として使います。

### Catalog Management

`catalog.add_from_dict()`、`catalog.add_from_file()`、`catalog.add_from_dir()`、`catalog.add_from_package_file()`、`catalog.add_from_package_dir()`、`catalog.clear()` を利用できます。

### Functional API

#### `get_system_language() -> Language`

system language を BCP 47 language tag として検出し、検出できない場合や C/POSIX locale の場合は `"en"` にフォールバックします。

#### `get_translator(language: str, scope: str) -> Translator`

指定 language / scope の translator を返します。

### `Translator(catalog, language, scope, default_language="en")`

translation key と template variables を受け取り、翻訳済み文字列を返します。

### Translation Behavior

指定 language に key がない場合は、`zh-Hant-TW -> zh-Hant -> zh` のように parent tag を参照します。それでもない場合は default language とその parent tag を参照し、最後に default value や key を使います。

## Configuration

### Catalog Management

YAML file や dictionary から catalog を読み込めます。複数 catalog の merge にも対応します。

### Settings Configuration

設定管理には pydantic-settings-manager を利用できます。

### Settings Fields

catalog loading や default language など、application 側の設定に合わせて管理できます。

## Testing

```bash
mise run package:test kiarina-i18n
mise run package:test kiarina-i18n --coverage
```

## Dependencies

- `pydantic`
- `pydantic-settings`
- `pydantic-settings-manager`
- `pyyaml`

## License

MIT License です。詳細は [LICENSE](../../LICENSE) を参照してください。

## Related Projects

- [kiarina-python](https://github.com/kiarina/kiarina-python)
- [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager)
