# kiarina-i18n

Simple internationalization (i18n) utilities for Python applications.

## Purpose

`kiarina-i18n` provides a lightweight and straightforward approach to internationalization in Python applications.
It focuses on simplicity and predictability, avoiding complex grammar rules or plural forms.

For applications requiring advanced features like plural forms or complex localization,
consider using established tools like `gettext`.

## Installation

```bash
pip install kiarina-i18n
```

## Quick Start

### Basic Usage (Functional API)

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

### Type-Safe Class-Based API (Recommended)

For better type safety and IDE support, use the class-based API:

```python
from kiarina.i18n import I18n, get_i18n, settings_manager

# Define your i18n class with explicit scope
class AppI18n(I18n, scope="app.greeting"):
    hello: str = "Hello, $name!"
    goodbye: str = "Goodbye!"
    welcome: str = "Welcome to our app!"

# Or let scope be auto-generated from module.class_name
# If defined in my_app/i18n.py, scope will be: my_app.i18n.UserProfileI18n
class UserProfileI18n(I18n):
    name: str = "Name"
    email: str = "Email"
    bio: str = "Biography"

# Configure the catalog
settings_manager.user_config = {
    "catalog": {
        "ja": {
            "app.greeting": {
                "hello": "こんにちは、$name!",
                "goodbye": "さようなら!",
                "welcome": "アプリへようこそ!"
            }
        }
    }
}

# Get translated instance
t = get_i18n(AppI18n, "ja")

# Access translations with full type safety and IDE completion
print(t.hello)     # Output: こんにちは、$name!
print(t.goodbye)   # Output: さようなら!
print(t.welcome)   # Output: アプリへようこそ!

# Template variables are handled by the functional API
from kiarina.i18n import get_translator
translator = get_translator("ja", "app.greeting")
print(translator("hello", name="World"))  # Output: こんにちは、World!
```

**Benefits of Class-Based API:**
- **Type Safety**: IDE detects typos in field names
- **Auto-completion**: IDE suggests available translation keys
- **Self-documenting**: Class definition serves as documentation
- **Default Values**: Explicit fallback values when translation is missing
- **Immutable**: Translation instances are frozen and cannot be modified
- **Clean Syntax**: Scope is defined at class level, not as a field

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

### Pydantic Integration for LLM Tools

For LLM tool schemas, kiarina-i18n provides two complementary functions:

1. **`create_pydantic_schema`**: Creates a schema with descriptions from an I18n model (used at tool definition time)
2. **`translate_pydantic_model`**: Translates the schema to different languages (used at runtime)

#### Recommended Pattern: Static Definition + Dynamic Translation

This pattern defines the tool once with default descriptions, then translates it dynamically at runtime:

```python
from pydantic import BaseModel
from langchain.tools import BaseTool, tool
from kiarina.i18n import I18n, get_i18n, settings_manager
from kiarina.i18n_pydantic import create_pydantic_schema, translate_pydantic_model

# Step 1: Define all translations in one I18n class
class HogeI18n(I18n, scope="hoge"):
    """Hoge tool for processing data."""

    # Fields for tool arguments (used in schema)
    name: str = "Your Name"
    age: str = "Your Age"

    # Additional translations for runtime logic
    note: str = "This is a note."
    error_message: str = "Error: file not found."

# Step 2: Define argument schema (structure only)
class ArgsSchema(BaseModel):
    name: str
    age: int

# Step 3: Define tool with default descriptions (static)
@tool(args_schema=create_pydantic_schema(ArgsSchema, HogeI18n))
def hoge_tool(name: str, age: int) -> str:
    """Process user data"""
    return f"Processed: {name}"

# Step 4: Configure translations
settings_manager.user_config = {
    "catalog": {
        "ja": {
            "hoge": {
                "__doc__": "データ処理用のHogeツール。",
                "name": "あなたの名前",
                "age": "あなたの年齢",
                "note": "これはメモです。",
                "error_message": "エラー: ファイルが見つかりません。",
            }
        },
        "en": {
            "hoge": {
                "__doc__": "Hoge tool for processing data.",
                "name": "Your Name",
                "age": "Your Age",
                "note": "This is a note.",
                "error_message": "Error: file not found.",
            }
        }
    }
}

# Step 5: Create language-specific tools at runtime (dynamic)
def get_tool(language: str) -> BaseTool:
    """Get tool with translated schema for the specified language."""
    # Translate the schema
    translated_schema = translate_pydantic_model(hoge_tool.args_schema, language)
    
    # Create a copy of the tool with translated schema
    translated_tool = hoge_tool.model_copy(update={"args_schema": translated_schema})
    
    return translated_tool

# Step 6: Use language-specific tools
tool_ja = get_tool("ja")  # Japanese version
tool_en = get_tool("en")  # English version

# The tool schema will have language-specific descriptions
schema_ja = tool_ja.args_schema.model_json_schema()
print(tool_ja.args_schema.__doc__)  # "データ処理用のHogeツール。"
print(schema_ja["properties"]["name"]["description"])  # "あなたの名前"

schema_en = tool_en.args_schema.model_json_schema()
print(tool_en.args_schema.__doc__)  # "Hoge tool for processing data."
print(schema_en["properties"]["name"]["description"])  # "Your Name"

# Use I18n for runtime translations in tool logic
def enhanced_hoge_tool(name: str, age: int, language: str) -> str:
    """Enhanced tool with runtime translations"""
    t = get_i18n(HogeI18n, language)
    
    if not file_exists:
        raise Exception(t.error_message)
    
    return f"Processed: {name}"
```

**Benefits:**
- **Static Definition**: Tool is defined once with `create_pydantic_schema`
- **Dynamic Translation**: Schema is translated at runtime with `translate_pydantic_model`
- **Unified I18n**: All translations (tool args + runtime messages) in one I18n class
- **Type Safety**: IDE completion for both schema fields and runtime translations
- **Clean Separation**: Schema structure (ArgsSchema) separate from descriptions (HogeI18n)
- **Easy Translation**: Single catalog entry covers all translations

## API Reference

### Class-Based API

#### `I18n`

Base class for defining i18n translations with type safety.

**Usage:**
```python
from kiarina.i18n import I18n

# Explicit scope
class MyI18n(I18n, scope="my.module"):
    title: str = "Default Title"
    description: str = "Default Description"

# Auto-generated scope (from module.class_name)
# If defined in my_app/i18n.py, scope will be: my_app.i18n.UserProfileI18n
class UserProfileI18n(I18n):
    name: str = "Name"
    email: str = "Email"
```

**Features:**
- **Immutable**: Instances are frozen and cannot be modified
- **Type-safe**: Full type hints and validation
- **Self-documenting**: Field names are translation keys, field values are defaults
- **Clean Syntax**: Scope is defined at class level using inheritance parameter
- **Auto-scope**: Automatically generates scope from module and class name if not provided

#### `get_i18n(i18n_class: type[T], language: str) -> T`

Get a translated i18n instance.

**Parameters:**
- `i18n_class`: I18n class to instantiate (not instance!)
- `language`: Target language code (e.g., "en", "ja")

**Returns:**
- Translated i18n instance with all fields translated

**Example:**
```python
from kiarina.i18n import I18n, get_i18n

class AppI18n(I18n, scope="app"):
    title: str = "My App"

t = get_i18n(AppI18n, "ja")
print(t.title)  # Translated title
```

### Pydantic Schema Creation (kiarina.i18n_pydantic)

#### `create_pydantic_schema(pydantic_model: type[T], i18n_model: type[I18n]) -> type[I18n]`

Create a Pydantic schema with field descriptions from I18n model.

This function creates a new I18n subclass that:
- Copies field structure from `pydantic_model`
- Sets field descriptions from `i18n_model`'s default values
- Uses `i18n_model`'s `__doc__` as the schema's docstring
- Inherits `i18n_model`'s scope for translation

**Parameters:**
- `pydantic_model`: Source Pydantic model to copy field structure from
- `i18n_model`: I18n model containing default descriptions and scope

**Returns:**
- New I18n subclass with combined structure and descriptions

**Example:**
```python
from pydantic import BaseModel
from kiarina.i18n import I18n, create_pydantic_schema

class HogeI18n(I18n, scope="hoge"):
    """Hoge tool"""
    name: str = "Your Name"
    age: str = "Your Age"

class ArgsSchema(BaseModel):
    name: str
    age: int

# Create schema with descriptions from I18n
Schema = create_pydantic_schema(ArgsSchema, HogeI18n)

# Schema now has:
# - __doc__ = "Hoge tool"
# - name field with description "Your Name"
# - age field with description "Your Age"
# - _scope = "hoge"
```

### Pydantic Model Translation (kiarina.i18n_pydantic)

#### `translate_pydantic_model(model: type[T], language: str, scope: str | None = None) -> type[T]`

Translate Pydantic model field descriptions.

**Parameters:**
- `model`: Pydantic model class to translate
- `language`: Target language code (e.g., "ja", "en")
- `scope`: Translation scope (e.g., "hoge.fields"). Optional if `model` is an `I18n` subclass (automatically uses `model._scope`)

**Returns:**
- New model class with translated field descriptions

**Example:**
```python
from pydantic import BaseModel, Field
from kiarina.i18n import I18n, translate_pydantic_model

# With explicit scope (for regular BaseModel)
class Hoge(BaseModel):
    name: str = Field(description="Your Name")

HogeJa = translate_pydantic_model(Hoge, "ja", "hoge.fields")

# With I18n subclass (scope auto-detected)
class HogeI18n(I18n, scope="hoge.fields"):
    name: str = "Your Name"

HogeI18nJa = translate_pydantic_model(HogeI18n, "ja")  # scope is optional
```

### Cache Management

#### `clear_cache() -> None`

Clear all i18n-related caches.

This function clears the internal caches used by `get_catalog()` and `get_translator()`. Useful when you need to reload configuration or reset state during testing.

**Example:**
```python
from kiarina.i18n import clear_cache, settings_manager

# Change settings
settings_manager.user_config = {"catalog": {...}}

# Clear caches to apply new settings
clear_cache()
```

### Functional API

#### `get_catalog() -> Catalog`

Get the translation catalog from settings.

This function is cached to avoid loading the catalog multiple times. It can be used independently for custom translation logic or direct catalog access.

**Returns:**
- `Catalog`: Translation catalog loaded from file or settings

**Example:**
```python
from kiarina.i18n import get_catalog, settings_manager

# Configure catalog
settings_manager.user_config = {
    "catalog": {
        "en": {"app.greeting": {"hello": "Hello!"}},
        "ja": {"app.greeting": {"hello": "こんにちは!"}}
    }
}

# Get catalog
catalog = get_catalog()
print(catalog["en"]["app.greeting"]["hello"])  # "Hello!"

# Use for custom translation logic
def custom_translate(lang: str, scope: str, key: str) -> str:
    return catalog.get(lang, {}).get(scope, {}).get(key, "")

print(custom_translate("ja", "app.greeting", "hello"))  # "こんにちは!"
```

#### `get_translator(language: str, scope: str) -> Translator`

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
