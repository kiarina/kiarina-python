---
title: About kiarina-utils-common package
description: >-
  kiarina-utils-common provides common utility functions
  including configuration string parsing and dynamic object importing.
---

kiarina-utils-common provides essential utility functions for the kiarina namespace packages.
This package includes commonly used helper functions that are shared across multiple kiarina packages.

Key features include:
- Configuration string parser with nested keys and array indices support
- Dynamic object import from import paths (useful for plugin systems)
- Automatic type conversion (bool, int, float, str)
- Type-safe utilities built with Pydantic

Main utilities:
- `parse_config_string()`: Parse configuration strings into nested dictionaries
- `import_object()`: Import objects (classes, functions, constants) dynamically from import paths
