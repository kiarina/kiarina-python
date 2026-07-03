# Package README Structure

English | [日本語](README.ja.md)

This document defines the standard heading structure for each package's `README.md` and `README.ja.md`.

## Principles

- Maintain `README.md` and `README.ja.md` as complete mirrors in different languages.
- Use the same English headings, hierarchy, and order in both files.
- Organize headings so readers can understand the package's dependencies, installation, primary use cases, and public APIs in that order.
- Document public APIs by the public import paths used by consumers, not by the internal file structure.
- Document every public API signature, including parameters, parameter types, defaults, and return types.
- Omit headings that have no package-specific content instead of leaving them empty.

## Standard Structure

Use the following order as the standard for regular library packages.

```markdown
# <package-name>

English | [日本語](README.ja.md)

<badges>

> [!NOTE] What is this?
> <Describe the package's role in one sentence>

## Dependencies

### Required Dependencies

### Optional Dependencies

#### `<extra-name>`

## Installation

## Features

### <Use Case or Feature>

## API Reference

### `<Public Import Path>`

#### `<Public API>`
```

Use the following language switcher in the Japanese version.

```markdown
[English](README.md) | 日本語
```

## Required Sections

### Package Title

Use the PyPI package name as the H1.

```markdown
# kiarina-utils-common
```

Place the language switcher, badges such as PyPI, Python, and License, and a NOTE describing the package's role immediately after the title.

The NOTE should explain what the package provides in one sentence rather than list its detailed features.

### Dependencies

List runtime dependencies installed for consumers in a table.
If optional dependencies are available, use separate tables for required and optional dependencies.

```markdown
## Dependencies

### Required Dependencies

| Package | Version | License |
| --- | --- | --- |
| [Pydantic](https://github.com/pydantic/pydantic) | `>=2.0.0` | [MIT](https://github.com/pydantic/pydantic/blob/main/LICENSE) |

### Optional Dependencies

#### `mime`

Used for content-based MIME type detection.

| Package | Version | License |
| --- | --- | --- |
| [puremagic](https://github.com/cdgriffith/puremagic) | `>=1.30` | [MIT](https://github.com/cdgriffith/puremagic/blob/main/LICENSE) |
```

Create a separate H4 and table for each Extra, and briefly describe its purpose.
If there are no optional dependencies, the `Required Dependencies` heading may be omitted.
If the package only uses the Python standard library, state that briefly.
Do not include development or test dependencies.

### Installation

Show the minimum command for installing the individual package from PyPI.

````markdown
## Installation

```bash
pip install <package-name>
```
````

If Extras are available, also show the installation command for each Extra.

````markdown
```bash
pip install "<package-name>[<extra-name>]"
```
````

### Features

Describe what consumers can accomplish, organized by use case.
Start with a feature list, then add an H3 with the same name for each item that needs a detailed explanation.

```markdown
## Features

- **<Use Case>**
  <What consumers can accomplish>

### <Use Case>

<Explanation and executable example>
```

Prefer headings that communicate the consumer's goal rather than only internal class or module names.
Import from public APIs in code examples and keep their prerequisites minimal.

### API Reference

Document the package's public APIs under the public import paths used by consumers.
For modules that define `__all__`, use its contents as the public API boundary.

Cover all of the following public elements:

- Functions
- Class constructors
- All public class methods and properties
- Public instances
- Public data types and fields, including data classes and `NamedTuple`
- Type aliases
- Callable and interface types such as `Protocol`

For every function, constructor, method, property, and callable, include the complete signature with parameter names, parameter types, defaults, and return types. Minimal usage without type annotations does not replace the signature.

````markdown
## API Reference

### `<Public Import Path>`

```python
from <public.import.path> import (
    <PublicAPI>,
)
```

#### `<Public API>`

```python
def <function>(
    <argument>: <type>,
    *,
    <optional_argument>: <type> = <default>,
) -> <return_type>: ...
```

<Summary>

**Parameters**

- `<name>` (`<type>`): <Description>

**Returns**

- `<type>`: <Description>

**Raises**

- `<Exception>`: <Condition>

**Examples**

```python
<example>
```
````

Omit items that do not apply.
Add descriptions, exceptions, and examples only when they help consumers understand the API.
Within each public import path, list basic functions first, followed by primary classes and supporting types or instances.

Class constructors and all public methods may be documented together.

```python
class Registry(Generic[T]):
    def __init__(
        self,
        *,
        expected_type: type[T],
    ) -> None: ...

    def get(self, name: str | None = None) -> T: ...

    def clear(self) -> None: ...
```

Keep signatures and the executable content of code examples identical between `README.md` and `README.ja.md`; translate only explanatory prose and comments.
