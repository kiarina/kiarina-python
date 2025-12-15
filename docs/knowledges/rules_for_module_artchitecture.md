---
title: Module Architecture Rules
description: This document explains the design principles for this Python project.
---

# Module Architecture Rules

## One Public Element Per File

Each file should contain only one public class, function, type, or constant.
Private elements may be grouped together in the same file.

## Implement Features in Subpackages

Do not implement features directly in the top-level `kiarina` package.
Create appropriate subpackages under the `kiarina` namespace and implement features within those subpackages.
Nesting is allowed.
Parent packages of feature-implementing subpackages should not implement features themselves, but should only be used for grouping subpackages.

Use uv workspace and namespace packages to enable proper grouping and distribution of these subpackages.
A single distribution unit may contain multiple subpackages, or a single subpackage may be a single distribution unit.

## File Structure Within Subpackages

Subpackages should have the following file structure:

```
hoge/fuga/
  __init__.py           # Import public elements of the subpackage and register them in __all__
  _settings.py          # Pydantic Settings, Settings Manager
  _constants/           # Constants
    __init__.py         # Leave empty with no comments. __init__.py files below the top level of submodules should be empty
    some_constant.py
  _enums/               # Enums
  _helpers/             # Helper functions that provide subpackage functionality to external users
    __init__.py
    create_fuga.py
  _models/              # Data models containing business logic (Pydantic models or dataclasses)
    fuga.py
  _operations/          # Modules to separate heavy logic from subpackages to improve readability (function-based separation, for internal calls)
  _schemas/             # Data structure definitions without business logic (Pydantic models or dataclasses)
  _services/            # Modules implementing business logic for subpackages (class-based separation)
  _types/               # Type definitions for subpackages (TypeAlias, TypeVar, TypedDict, etc.)
  _utils/               # Pure, stateless, highly reusable utilities that don't depend on subpackage features
  _views/               # Data structure definitions for interface interactions (Pydantic models or dataclasses) (mainly for external calls)
```

Directories under subpackages should be prefixed with `_` to indicate they are internal implementations of the subpackage.

### Example of _settings.py

```python
from pydantic_settings import BaseSettings
from pydantic_settings_manager import SettingsManager

class FugaSettings(BaseSettings):
    api_key: str
    timeout: int = 30

settings_manager = SettingsManager(FugaSettings)
```

Export `FugaSettings` and `settings_manager` in `__init__.py`.

### Example of __init__.py

```python
from ._constants.some_constant import SOME_CONSTANT
from ._helpers.create_fuga import create_fuga
from ._models.fuga import Fuga
from ._settings import FugaSettings, settings_manager

__all__ = [
    # ._constants
    "SOME_CONSTANT",
    # ._helpers
    "create_fuga",
    # ._models
    "Fuga",
    # ._settings
    "FugaSettings",
    "settings_manager",
]
```

When lazy imports are needed, implement as follows:

```python
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ._constants.some_constant import SOME_CONSTANT
    from ._helpers.create_fuga import create_fuga
    from ._models.fuga import Fuga
    from ._settings import FugaSettings, settings_manager

__all__ = [
    # ._constants
    "SOME_CONSTANT",
    # ._helpers
    "create_fuga",
    # ._models
    "Fuga",
    # ._settings
    "FugaSettings",
    "settings_manager",
]

def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._constants
        "SOME_CONSTANT": "._constants.some_constant",
        # ._helpers
        "create_fuga": "._helpers.create_fuga",
        # ._models
        "Fuga": "._models.fuga",
        # ._settings
        "FugaSettings": "._settings",
        "settings_manager": "._settings",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
```

`__init__.py` files below the top level of submodules should be left empty with no comments.

## Dependencies

Dependencies between modules within subpackages should be designed in the following order:

**Layer 1 (Top)**
- _helpers

**Layer 2**
- _models
- _operations
- _services

**Layer 3**
- _constants
- _settings

**Layer 4**
- _schemas
- _views

**Layer 5 (Bottom)**
- _enums
- _types
- _utils

Dependencies from upper layers to lower layers are allowed, but not vice versa.
Within the same layer, the direction of dependencies may vary depending on the content of the submodules.
However, dependencies must always be unidirectional.

## Supporting Both Synchronous and Asynchronous

When supporting both synchronous and asynchronous in a submodule, the file structure should be as follows:

```
hoge/fuga/
  __init__.py        # Import public elements of the synchronous version and register them in __all__
  asyncio.py         # Import public elements of the asynchronous version and register them in __all__
  _settings.py       # Pydantic Settings, Settings Manager
  _async/            # Asynchronous version submodules
    __init__.py
    helpers/
      get_fuga.py
  _core/             # Core logic common to both synchronous and asynchronous
    __init__.py
    helpers/
      get_fuga.py
    schemas/
      fuga.py
  _sync/             # Synchronous version submodules
    __init__.py
    helpers/
      get_fuga.py
```

The contents of `_async/`, `_core/`, and `_sync/` should follow the file structure within subpackages described above.

### Example of __init__.py (Synchronous Version)

```python
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ._core._schemas.fuga import Fuga
    from ._sync._helpers.get_fuga import get_fuga

__all__ = [
    # ._core._schemas
    "Fuga",
    # ._sync._helpers
    "get_fuga",
]

def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._core._schemas
        "Fuga": "._core._schemas.fuga",
        # ._sync._helpers
        "get_fuga": "._sync._helpers.get_fuga",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
```

### Example of asyncio.py (Asynchronous Version)

```python
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ._async._helpers.get_fuga import get_fuga
    from ._core._schemas.fuga import Fuga

__all__ = [
    # ._async._helpers
    "get_fuga",
    # ._core._schemas
    "Fuga",
]

def __getattr__(name: str) -> object:
    if name not in __all__:  # pragma: no cover
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        # ._async._helpers
        "get_fuga": "._async._helpers.get_fuga",
        # ._core._schemas
        "Fuga": "._core._schemas.fuga",
    }

    parent = __name__.rsplit(".", 1)[0]
    globals()[name] = getattr(import_module(module_map[name], parent), name)
    return globals()[name]
```

### Example of _core/_helpers/get_fuga.py

```python
from typing import Awaitable, Literal, overload
from .._schemas.fuga import Fuga

@overload
def get_fuga(mode: Literal["sync"]) -> Fuga: ...

@overload
def get_fuga(mode: Literal["async"]) -> Awaitable[Fuga]: ...

def get_fuga(mode: Literal["sync", "async"]) -> Fuga | Awaitable[Fuga]:
    def _sync() -> Fuga:
        return Fuga(name="synchronous fuga")

    async def _async() -> Fuga:
        return Fuga(name="asynchronous fuga")

    if mode == "sync":
        return _sync()
    else:
        return _async()
```

### Example of _async/_helpers/get_fuga.py

```python
from ..._core._helpers.get_fuga import get_fuga

async def get_fuga() -> Fuga:
    return await get_fuga("async")
```

### Example of _sync/_helpers/get_fuga.py

```python
from ..._core._helpers.get_fuga import get_fuga

def get_fuga() -> Fuga:
    return get_fuga("sync")
```

This method is the best, but when using libraries that don't natively support asynchronous operations,
you can also create a synchronous version and wrap it with `asyncio.to_thread` for the asynchronous version.

## About Plugin Patterns

When using plugin patterns, separate the abstraction layer and implementation layer submodules.

```
hoge/fuga/
  __init__.py           # Import public elements of the abstraction layer and register them in __all__
  _settings.py          # Make the import path of implementations configurable
  _helpers/
    __init__.py
    create_fuga.py      # Factory function to create Fuga
  _models/
    __init__.py
    base_fuga.py        # class BaseFuga(Fuga, ABC) - define base class if needed
  _types/
    __init__.py
    fuga.py             # class Fuga(Protocol)
hoge/fuga_impl/
  __init__.py           # Implementation classes are dynamically retrieved by import path, so don't export in __init__.py
  blue.py               # Implement class BlueFuga(BaseFuga)
  red.py                # Implement class RedFuga(BaseFuga)
  README.md             # Explanation of file structure
```

### Example of _helpers/create_fuga.py

```python
from importlib import import_module

from .._settings import settings_manager
from .._types.fuga import Fuga

def create_fuga(settings_key: str) -> Fuga:
    settings = settings_manager.get_settings(settings_key)
    import_path = settings.import_path

    if ":" in import_path:
        module_name, object_name = import_path.split(":", 1)
    else:
        module_name = import_path
        object_name = "Fuga"

    try:
        module = import_module(module_name)

    except ImportError:
        raise ImportError(
            f"Could not import file builder module '{module_name}' for config key '{settings_key}'."
        )

    if not hasattr(module, object_name):
        raise AttributeError(
            f"Module '{module_name}' does not have a '{object_name}' attribute for config key '{settings_key}'."
        )

    if not callable(getattr(module, object_name)):
        raise TypeError(
            f"Attribute '{object_name}' in module '{module_name}' is not callable for config key '{settings_key}'."
        )

    return getattr(module, object_name)()
```

## When Adopting Special File Structures

Like `hoge/fuga_impl/` in plugin patterns,
there may be cases where you want to partially adopt special file structures depending on the app or submodule.
In such cases, place a `README.md` in the directory adopting the special file structure and describe the explanation of the special file structure.

### Example of hoge/fuga_impl/README.md

```markdown
---
title: File Structure of hoge.fuga_impl Module
description: Implementation classes of hoge.fuga.Fuga are placed under hoge.fuga_impl.
---

In the `hoge/fuga_impl/` directory, implementation classes of `hoge.fuga.Fuga` are placed as follows:

hoge/fuga_impl/
  __init__.py        # Implementation classes are dynamically retrieved by import path, so don't export in __init__.py
  blue.py            # Implement class BlueFuga(Fuga)
  red.py             # Implement class RedFuga(Fuga)

File names should be the lowercase prefix of the implementation class name.
```

Create a `README.md` like the above.
How to arrange files is important.
Always clarify the intent and strive to reduce the cognitive load of the project.

## Significance of This Design Principle

By strictly adhering to one public element per file and the file structure, there are the following advantages:

- You can grasp the functionality of the entire project just by looking at the file tree
- The responsibilities of functions and classes can be clearly understood from the file path
- The need for redesign or module splitting becomes clear as the number of files increases

These allow you to reduce the cognitive load of the project as much as possible.
By unifying the structure, the file tree will become beautiful.

Programming is Elegant.
