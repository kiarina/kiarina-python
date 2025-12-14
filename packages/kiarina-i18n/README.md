# kiarina-i18n

Simple internationalization (i18n) utilities for Python applications.

## Purpose

`kiarina-i18n` provides a lightweight and straightforward approach to internationalization in Python applications. It focuses on simplicity and predictability, avoiding complex grammar rules or plural forms. For applications requiring advanced features like plural forms or complex localization, consider using established tools like `gettext`.

## Installation

```bash
pip install kiarina-i18n
```

## Quick Start

### Basic Usage

```python
from kiarina.i18n import get_translator, settings_manager

# Configure the catalog
settings_manager.user_config = {
    "catalog": {
        "en": {
            "app.greeting": {
                "hello": "Hello, $name!",
                "goodbye": "Goodbye!"
            }
        },
        "ja": {
            "app.greeting": {
                "hello": "こんにちは、$name!",
                "goodbye": "さようなら!"
            }
        }
    }
}

# Get a translator
t = get_translator("ja", "app.greeting")

# Translate with template variables
print(t("hello", name="World"))  # Output: こんにちは、World!
print(t("goodbye"))  # Output: さようなら!
```

### Using Catalog File

```python
from kiarina.i18n import get_translator, settings_manager

# Load catalog from YAML file
settings_manager.user_config = {
    "catalog_file": "i18n_catalog.yaml"
}

t = get_translator("en", "app.greeting")
print(t("hello", name="Alice"))
```

Example `i18n_catalog.yaml`:

```yaml
en:
  app.greeting:
    hello: "Hello, $name!"
    goodbye: "Goodbye!"
ja:
  app.greeting:
    hello: "こんにちは、$name!"
    goodbye: "さようなら!"
```

## API Reference

### `get_translator(language: str, scope: str) -> Translator`

Get a translator for the specified language and scope.

**Parameters:**
- `language`: Target language code (e.g., "en", "ja", "fr")
- `scope`: Translation scope (e.g., "app.greeting", "app.error")

**Returns:**
- `Translator`: Translator instance configured for the specified language and scope

**Example:**
```python
t = get_translator("ja", "app.greeting")
```

### `Translator(catalog, language, scope, fallback_language="en")`

Translator class for internationalization support.

**Parameters:**
- `catalog`: Translation catalog mapping languages to scopes to keys to translations
- `language`: Target language for translation
- `scope`: Scope for translation keys
- `fallback_language`: Fallback language when translation is not found (default: "en")

**Methods:**
- `__call__(key, default=None, **kwargs)`: Translate a key with optional template variables

**Example:**
```python
from kiarina.i18n import Translator

catalog = {
    "en": {"app.greeting": {"hello": "Hello, $name!"}},
    "ja": {"app.greeting": {"hello": "こんにちは、$name!"}}
}

t = Translator(catalog=catalog, language="ja", scope="app.greeting")
print(t("hello", name="World"))  # Output: こんにちは、World!
```

### Translation Behavior

1. **Primary lookup**: Searches for the key in the target language
2. **Fallback lookup**: If not found, searches in the fallback language
3. **Default value**: If still not found, uses the provided default value
4. **Error handling**: If no default is provided, returns `"{scope}#{key}"` and logs an error

## Configuration

### Using pydantic-settings-manager

```yaml
# config.yaml
kiarina.i18n:
  default_language: "en"
  catalog:
    en:
      app.greeting:
        hello: "Hello, $name!"
    ja:
      app.greeting:
        hello: "こんにちは、$name!"
```

```python
from pydantic_settings_manager import load_user_configs
import yaml

with open("config.yaml") as f:
    config = yaml.safe_load(f)

load_user_configs(config)
```

### Settings Fields

- `default_language` (str): Default language to use when translation is not found (default: "en")
- `catalog_file` (str | None): Path to YAML file containing translation catalog
- `catalog` (dict): Translation catalog mapping languages to scopes to keys to translations

## Testing

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=kiarina.i18n --cov-report=html
```

## Dependencies

- `pydantic>=2.0.0`
- `pydantic-settings>=2.0.0`
- `pydantic-settings-manager>=2.3.0`
- `pyyaml>=6.0.0`

## License

This project is licensed under the MIT License - see the [LICENSE](../../LICENSE) file for details.

## Related Projects

- [kiarina-python](https://github.com/kiarina/kiarina-python) - Parent monorepo containing all kiarina packages
