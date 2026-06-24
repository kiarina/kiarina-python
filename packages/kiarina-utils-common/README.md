# kiarina-utils-common

English | [日本語](README.ja.md)

[![PyPI version](https://badge.fury.io/py/kiarina-utils-common.svg)](https://badge.fury.io/py/kiarina-utils-common)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-utils-common.svg)](https://pypi.org/project/kiarina-utils-common/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

The package providing the most general-purpose utilities in the kiarina namespace.

## Installation

```bash
pip install kiarina-utils-common
```

## API Reference

### `import_object`

```python
import_object(import_path)
```

Import and return an object from an import path.

**Parameters**

- `import_path` (`str`): Import path in the format `module_name:object_name`
  - Example: `kiarina.utils.common:parse_config_string`

**Returns**

- The imported object (class, function, or any other object)

**Raises**

- `ValueError`: If import_path format is invalid
- `ImportError`: If the module cannot be imported
- `AttributeError`: If the object doesn't exist in the module

**Examples**

```python
# Import a function
parse_fn = import_object('kiarina.utils.common:parse_config_string')
result = parse_fn('key=value')

# Import a class
MyClass = import_object('myapp.plugins:MyPlugin')
instance = MyClass()

# Use with type hints
from typing import Callable
parser: Callable = import_object('kiarina.utils.common:parse_config_string')
```

### `parse_config_string`

```python
parse_config_string(
    config_str,
    *,
    separator="&",
    key_value_separator="=",
    nested_separator=".",
    brackets="()",
)
```

Parse configuration string into nested dictionary.

**Parameters**

- `config_str` (`str`): Configuration string to parse
- `separator` (`str`, optional): Item separator. Default: `"&"`
- `key_value_separator` (`str`, optional): Key-value separator. Default: `"="`
- `nested_separator` (`str`, optional): Nested key separator. Default: `"."`
- `brackets` (`str`, optional): Two-character open/close pair for quoting values that contain separator characters. Default: `"()"`. Pass `""` to disable.

**Returns**

- `dict[str, Any]`: Parsed configuration dictionary

**Examples**

```python
# Basic usage
parse_config_string("key1=value1&key2=value2")
# {"key1": "value1", "key2": "value2"}

# Nested keys
parse_config_string("cache.enabled=true&db.port=5432")
# {"cache": {"enabled": True}, "db": {"port": 5432}}

# Flags (no value)
parse_config_string("debug&verbose")
# {"debug": None, "verbose": None}

# Bracketed values (verbatim, type-conversion suppressed)
parse_config_string("k=(a&b=c)&n=5")
# {"k": "a&b=c", "n": 5}

# Custom separators
parse_config_string("a:1;b:2", separator=";", key_value_separator=":")
# {"a": 1, "b": 2}
```

### `ConfigRegistry`

Manage configurations by name, alias, and default, with overrides from configuration strings or keyword arguments. Resolved configurations are deep-copied so the registered sources remain unchanged.

```python
from kiarina.utils.config_registry import ConfigRegistry

registry = ConfigRegistry[dict[str, object]](
    get_default=lambda: "standard",
    get_aliases=lambda: {"default": "standard"},
    get_presets=lambda: {
        "standard": {"model": "example", "temperature": 0.5},
    },
)

config = registry.get("default?temperature=0.8")
# {"model": "example", "temperature": 0.8}

resolved = registry.resolve("standard")
print(resolved.name)
print(resolved.config)
```

**Key methods**

- `register(name, config)` / `unregister(name)`: Register or remove a runtime configuration
- `get(specifier=None, **kwargs)`: Return a resolved configuration
- `resolve(specifier=None, **kwargs)`: Return the resolved name and configuration as `ResolvedConfig`
- `list_names()` / `list_aliases()`: List available names and aliases
- `clear()`: Remove runtime configurations

### `ComponentRegistry`

Manage classes and factories by name and create a new instance when needed. Preset and custom components may also be defined using import paths.

```python
from kiarina.utils.component_registry import ComponentRegistry


class Client:
    def __init__(self, endpoint: str = "") -> None:
        self.endpoint = endpoint


registry = ComponentRegistry(expected_type=Client)
registry.register("client", Client)

client = registry.resolve("client?endpoint=https://example.com")
```

**Key methods**

- `register(name, factory)` / `unregister(name)`: Register or remove a component factory
- `create(name, *args, **kwargs)`: Create a new instance by name
- `resolve(input=None, *args, **kwargs)`: Resolve an instance or specifier
- `get(name)`: Return a runtime-registered factory
- `list_names()` / `list_aliases()`: List available names and aliases
- `clear()`: Remove runtime-registered factories

### `ObjectRegistry`

Resolve configurations through `ConfigRegistry` and create objects from them. `get()` retains and reuses created objects, while `create()` and `resolve()` return a new object each time.

```python
from kiarina.utils.object_registry import ObjectRegistry


class Client:
    def __init__(self, endpoint: str = "") -> None:
        self.endpoint = endpoint


registry = ObjectRegistry[Client, dict[str, object]](
    expected_type=Client,
    get_default=lambda: "default",
    get_presets=lambda: {
        "default": {"endpoint": "https://example.com"},
    },
)

shared_client = registry.get()
fresh_client = registry.resolve("default?endpoint=https://api.example.com")
```

**Key methods**

- `register(name, object)` / `unregister(name)`: Register or remove an object
- `get(name=None)`: Return an object, creating and retaining it when necessary
- `create(name, **kwargs)`: Create a new object from a configuration
- `resolve(input=None, **kwargs)`: Resolve an instance or configuration specifier into a new object
- `register_config(name, config)` / `unregister_config(name)`: Register or remove a runtime configuration
- `list_names()` / `list_aliases()`: List available names and aliases
- `clear()` / `clear_configs()`: Remove runtime objects or configurations
