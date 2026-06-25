# Package README Structure

English | [日本語](README.ja.md)

This document defines the standard heading structure for each package's `README.md` and `README.ja.md`.

## Principles

- Maintain `README.md` and `README.ja.md` as complete mirrors in different languages.
- Use the same English headings, hierarchy, and order in both files.
- Organize headings so readers can understand the package's dependencies, installation, primary use cases, and public APIs in that order.
- Document public APIs by the public import paths used by consumers, not by the internal file structure.
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

## Installation

## Features

### <Use Case or Feature>

## API Reference

### `<Public API>`
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

```markdown
## Dependencies

| Package | Version | License |
| --- | --- | --- |
| [Pydantic](https://github.com/pydantic/pydantic) | `>=2.0.0` | [MIT](https://github.com/pydantic/pydantic/blob/main/LICENSE) |
```

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

If optional dependencies are available, add an `### Optional Dependencies` subsection.

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

Document the package's public APIs by public element, such as functions, classes, and instances.

````markdown
## API Reference

### `<Public API>`

```python
<signature or minimal usage>
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
As a general ordering rule, list basic functions first, followed by primary classes and supporting types or instances.
