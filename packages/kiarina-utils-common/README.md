# kiarina-utils-common

English | [日本語](README.ja.md)

[![PyPI version](https://badge.fury.io/py/kiarina-utils-common.svg)](https://badge.fury.io/py/kiarina-utils-common)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-utils-common.svg)](https://pypi.org/project/kiarina-utils-common/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> [!NOTE] What is this?
> A package providing lightweight configuration resolution, dynamic imports, and registry foundations.

## Dependencies

| Package | Version | License |
| --- | --- | --- |
| [Pydantic](https://github.com/pydantic/pydantic) | `>=2.0.0` | [MIT](https://github.com/pydantic/pydantic/blob/main/LICENSE) |

## Installation

```bash
pip install kiarina-utils-common
```

## Features

- **Implementing a Plugin System**
  Build a plugin system that selects and dynamically creates implementations from configured import paths.
- **Managing a Singleton**
  Retain and reuse an object created from resolved configuration.

### Implementing a Plugin System

ComponentRegistry can be used to build a plugin system that selects and creates implementations from configured import paths.
The following example uses [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager).

```sh
sample/
  hoge/
    _instances/
      hoge_registry.py
    _services/
      base_hoge.py
    _types/
      hoge.py
      hoge_name.py
      hoge_alias.py
      hoge_specifier.py
    __init__.py
    _settings.py
  hoge_impl/
    vanilla/
      _helpers/
        create_vanilla_hoge.py
      _services/
        vanilla_hoge.py
      __init__.py
      _settings.py
```

**Define the abstraction:**
```python
# sample/hoge/_types/hoge_name.py
HogeName: TypeAlias = str

# sample/hoge/_types/hoge_alias.py
HogeAlias: TypeAlias = str

# sample/hoge/_types/hoge_specifier.py
HogeSpecifier: TypeAlias = str
"""{HogeName}[?{ConfigString}]"""

# sample/hoge/_types/hoge.py
@runtime_checkable
class Hoge(Protocol):
    name: HogeName
    def hello(self) -> None: ...

# sample/hoge/_services/base_hoge.py
class BaseHoge(Hoge):
    def __init__(self) -> None:
        self._name: HogeName | None = None

    @property
    def name(self) -> HogeName:
        if self._name is None:
            raise ValueError("name is not set")
        return self._name

    @name.setter
    def name(self, value: HogeName) -> None:
        self._name = value

# sample/hoge/_settings.py
class HogeSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SAMPLE_HOGE_",
        extra="ignore",
    )

    default: HogeSpecifier = "vanilla"

    aliases: dict[HogeAlias, HogeName] = Field(default_factory=dict)

    presets: dict[HogeName, ImportPath] = Field(
        default_factory=lambda: {
            "vanilla": "sample.hoge_impl.vanilla:create_vanilla_hoge",
        }
    )

    customs: dict[HogeName, ImportPath] = Field(default_factory=dict)

settings_manager = SettingsManager(HogeSettings)

# sample/hoge/_instances/hoge_registry.py
def _factory_wrapper(
    factory: ComponentFactory[Hoge],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> Hoge:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance

hoge_registry = ComponentRegistry[Hoge](
    expected_type=cast(type[Hoge], Hoge),
    component_label="Hoge",
    get_default=lambda: settings_manager.settings.default,
    get_aliases=lambda: settings_manager.settings.aliases,
    get_presets=lambda: settings_manager.settings.presets,
    get_customs=lambda: settings_manager.settings.customs,
    factory_wrapper=_factory_wrapper,
)

# sample/hoge/__init__.py
__all__ = [
    "BaseHoge",
    "Hoge",
    "HogeName",
    "HogeAlias",
    "HogeSpecifier",
    "settings_manager",
    "hoge_registry",
]
```

**Define the implementation:**
```python
# sample/hoge_impl/vanilla/_settings.py
class VanillaHogeSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SAMPLE_HOGE_VANILLA_",
        extra="ignore",
    )
    message: str = "Hello from VanillaHoge!"

settings_manager = SettingsManager(VanillaHogeSettings)

# sample/hoge_impl/vanilla/_services/vanilla_hoge.py
class VanillaHoge(BaseHoge):
    def __init__(self, settings: VanillaHogeSettings) -> None:
        super().__init__()
        self.settings: VanillaHogeSettings = settings

    def hello(self) -> None:
        print(self.settings.message)

# sample/hoge_impl/vanilla/_helpers/create_vanilla_hoge.py
def create_vanilla_hoge(**kwargs: Any) -> VanillaHoge:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = VanillaHogeSettings.model_validate(
            {**settings.model_dump(), **kwargs}
        )

    return VanillaHoge(settings)

# sample/hoge_impl/vanilla/__init__.py
__all__ = ["create_vanilla_hoge", "VanillaHoge", "settings_manager"]
```

**Usage:**
```python
hoge = hoge_registry.resolve()  # Get the default
hoge = hoge_registry.resolve("vanilla")  # Get a preset
hoge = hoge_registry.resolve("vanilla?message=Bye")  # Override with ConfigString
hoge.hello()
```

### Managing a Singleton

ObjectRegistry can retain and reuse an object created from resolved configuration.

**Define the registry:**
```python
from typing import Any

from kiarina.utils.object_registry import ObjectRegistry
from rich.console import Console


def _factory(name: str, config: dict[str, Any]) -> Console:
    return Console(**config)


console_registry = ObjectRegistry[Console, dict[str, Any]](
    expected_type=Console,
    object_label="Console",
    get_default=lambda: "default",
    get_presets=lambda: {
        "default": {"stderr": True, "highlight": False},
    },
    factory=_factory,
)
```

**Usage:**
```python
console1 = console_registry.get()  # Get the default
console2 = console_registry.get("default")  # Get a preset
console3 = console_registry.resolve("default?highlight=True")  # Override with ConfigString

console1.print("Hello, World!")
assert console1 is console_registry.get()  # Return the same object
```

## API Reference

### `kiarina.utils.common`

```python
from kiarina.utils.common import (
    ConfigString,
    ImportPath,
    import_object,
    parse_config_string,
)
```

#### `import_object`

```python
def import_object(import_path: ImportPath) -> Any: ...
```

Import and return an object from an import path in `module_name:object_name` format.

- `ValueError`: The import path format is invalid
- `ImportError`: The module cannot be imported
- `AttributeError`: The object does not exist in the module

#### `parse_config_string`

```python
def parse_config_string(
    config_str: ConfigString,
    *,
    separator: str = "&",
    key_value_separator: str = "=",
    nested_separator: str = ".",
    brackets: str = "()",
) -> dict[str, Any]: ...
```

Convert a configuration string into a nested dictionary.

Values are automatically converted to `bool`, `int`, or `float`. Keys without values become `None`, and numeric nested keys are treated as list indices. Values enclosed by `brackets` may contain separator characters and are not type-converted.

```python
parse_config_string(
    "enabled=true&ports.0=8000&ports.1=8001&plugin=(mock?delay=0.1)"
)
# {
#     "enabled": True,
#     "ports": [8000, 8001],
#     "plugin": "mock?delay=0.1",
# }
```

The function raises `ValueError` when `brackets` does not contain two characters, its opening and closing characters are identical, it conflicts with a separator, or brackets in the configuration string are unbalanced.

#### Type aliases

```python
type ConfigString = str
ImportPath: TypeAlias = str
```

| Type | Format |
| --- | --- |
| `ConfigString` | `key=value&key2=value2` |
| `ImportPath` | `module_name:object_name` |

### `kiarina.utils.config_registry`

```python
from kiarina.utils.config_registry import (
    ConfigAlias,
    ConfigName,
    ConfigRegistry,
    ConfigSpecifier,
    ResolvedConfig,
)
```

#### `ConfigRegistry`

Manage configurations by name, alias, and default, with overrides from configuration strings or keyword arguments. Resolved configurations are deep-copied so the registered sources remain unchanged.

```python
class ConfigRegistry(Generic[T]):
    def __init__(
        self,
        *,
        config_label: str = "Config",
        get_default: Callable[[], ConfigSpecifier | None] | None = None,
        get_aliases: Callable[[], dict[ConfigAlias, ConfigName]] | None = None,
        get_presets: Callable[[], dict[ConfigName, T]] | None = None,
        get_customs: Callable[[], dict[ConfigName, T]] | None = None,
        configure: Callable[[T, dict[str, Any]], T] | None = None,
    ) -> None: ...

    def get_default(self) -> ConfigSpecifier | None: ...

    def get_aliases(self) -> dict[ConfigAlias, ConfigName]: ...

    def list_aliases(self) -> list[ConfigAlias]: ...

    def list_names(self) -> list[ConfigName]: ...

    def register(self, config_name: ConfigName, config: T) -> None: ...

    def unregister(self, config_name: ConfigName) -> None: ...

    def is_registered(self, config_name: ConfigName) -> bool: ...

    def clear(self) -> None: ...

    def get(
        self,
        config_specifier: ConfigSpecifier | None = None,
        **kwargs: Any,
    ) -> T: ...

    def resolve(
        self,
        config_specifier: ConfigSpecifier | None = None,
        **kwargs: Any,
    ) -> ResolvedConfig[T]: ...
```

`get()` and `resolve()` search runtime registrations, custom configurations, and presets in that order. Without `configure`, overrides are supported for Pydantic `BaseModel` and `dict` values. Provide `configure` to override other value types.

#### `ResolvedConfig`

```python
class ResolvedConfig(NamedTuple, Generic[T]):
    name: ConfigName
    config: T
```

Contains the resolved configuration name and value.

#### Type aliases

```python
ConfigAlias: TypeAlias = str
ConfigName: TypeAlias = str
ConfigSpecifier: TypeAlias = str
```

`ConfigSpecifier` is a string in `{ConfigName|ConfigAlias}[?{ConfigString}]` format.

### `kiarina.utils.component_registry`

```python
from kiarina.utils.component_registry import (
    ComponentAlias,
    ComponentFactory,
    ComponentInput,
    ComponentName,
    ComponentRegistry,
    ComponentSpecifier,
)
```

#### `ComponentRegistry`

Manage classes and factories by name and create a new instance when needed. Preset and custom components may also be defined using import paths.

```python
class ComponentRegistry(Generic[T]):
    def __init__(
        self,
        *,
        expected_type: type[T],
        component_label: str = "Component",
        get_default: Callable[[], ComponentSpecifier | None] | None = None,
        get_aliases: Callable[
            [], dict[ComponentAlias, ComponentName]
        ] | None = None,
        get_presets: Callable[
            [], dict[ComponentName, ImportPath]
        ] | None = None,
        get_customs: Callable[
            [], dict[ComponentName, ImportPath]
        ] | None = None,
        factory_wrapper: Callable[
            [ComponentFactory[T], ComponentName, Any], T
        ] | None = None,
    ) -> None: ...

    def get_default(self) -> ComponentSpecifier | None: ...

    def get_aliases(self) -> dict[ComponentAlias, ComponentName]: ...

    def list_aliases(self) -> list[ComponentAlias]: ...

    def list_names(self) -> list[ComponentName]: ...

    def register(
        self,
        component_name: ComponentName,
        factory: ComponentFactory[T],
    ) -> None: ...

    def unregister(self, component_name: ComponentName) -> None: ...

    def get(
        self,
        component_name: ComponentName,
    ) -> ComponentFactory[T] | None: ...

    def clear(self) -> None: ...

    def create(
        self,
        component_name: ComponentName,
        *args: Any,
        **kwargs: Any,
    ) -> T: ...

    def resolve(
        self,
        component_input: ComponentInput[T] | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> T: ...
```

`create()` and `resolve()` always create a new instance and raise `ValueError` when it does not match `expected_type`. Factories are searched in runtime registrations, custom components, and presets in that order.

#### Type aliases

```python
ComponentAlias: TypeAlias = str
ComponentFactory: TypeAlias = Callable[..., T]
ComponentInput: TypeAlias = T | ComponentSpecifier
ComponentName: TypeAlias = str
ComponentSpecifier: TypeAlias = str
```

`ComponentSpecifier` is a string in `{ComponentName|ComponentAlias}[?{ConfigString}]` format.

### `kiarina.utils.object_registry`

```python
from kiarina.utils.object_registry import (
    ObjectAlias,
    ObjectFactory,
    ObjectInput,
    ObjectName,
    ObjectRegistry,
    ObjectSpecifier,
)
```

#### `ObjectRegistry`

Resolve configurations through `ConfigRegistry` and create objects from them. `get()` retains and reuses created objects, while `create()` and `resolve()` return a new object each time.

```python
class ObjectRegistry(Generic[TObject, TConfig]):
    def __init__(
        self,
        *,
        expected_type: type[TObject],
        object_label: str = "Object",
        get_default: Callable[[], ObjectSpecifier | None] | None = None,
        get_aliases: Callable[[], dict[ObjectAlias, ObjectName]] | None = None,
        get_presets: Callable[[], dict[ObjectName, TConfig]] | None = None,
        get_customs: Callable[[], dict[ObjectName, TConfig]] | None = None,
        configure: Callable[[TConfig, dict[str, Any]], TConfig] | None = None,
        factory: ObjectFactory[TObject, TConfig] | None = None,
    ) -> None: ...

    def get_default(self) -> ObjectSpecifier | None: ...

    def get_aliases(self) -> dict[ObjectAlias, ObjectName]: ...

    def register_config(
        self,
        object_name: ObjectName,
        config: TConfig,
    ) -> None: ...

    def unregister_config(self, object_name: ObjectName) -> None: ...

    def clear_configs(self) -> None: ...

    def is_config_registered(self, object_name: ObjectName) -> bool: ...

    def get_config(
        self,
        object_specifier: ObjectSpecifier | None = None,
    ) -> TConfig: ...

    def list_aliases(self) -> list[ObjectAlias]: ...

    def list_names(self) -> list[ObjectName]: ...

    def register(self, object_name: ObjectName, obj: TObject) -> None: ...

    def unregister(self, object_name: ObjectName) -> None: ...

    def clear(self) -> None: ...

    def is_registered(self, object_name: ObjectName) -> bool: ...

    def get(
        self,
        object_name: ObjectName | ObjectAlias | None = None,
    ) -> TObject: ...

    def create(
        self,
        object_name: ObjectName,
        **kwargs: Any,
    ) -> TObject: ...

    def resolve(
        self,
        object_input: ObjectInput[TObject] | None = None,
        **kwargs: Any,
    ) -> TObject: ...
```

`register()` and object creation validate that the value matches `expected_type`. `get()` does not accept a specifier containing a `ConfigString`. Use `create()` or `resolve()` to create a new object with configuration overrides.

#### `ObjectFactory`

```python
class ObjectFactory(Protocol[TObject_co, TConfig_contra]):
    def __call__(
        self,
        object_name: ObjectName,
        config: TConfig_contra,
        /,
    ) -> TObject_co: ...
```

A callable that receives the object name and configuration resolved by `ObjectRegistry` and creates an object.

#### Type aliases

```python
ObjectAlias: TypeAlias = str
ObjectInput: TypeAlias = TObject | ObjectSpecifier
ObjectName: TypeAlias = str
ObjectSpecifier: TypeAlias = str
```

`ObjectSpecifier` is a string in `{ObjectName|ObjectAlias}[?{ConfigString}]` format.
