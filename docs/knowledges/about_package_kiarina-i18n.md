---
title: About kiarina-i18n package
description: >-
  kiarina-i18n is a simple internationalization (i18n) library
  with configuration management using pydantic-settings-manager.
---

kiarina-i18n provides a lightweight and straightforward approach to internationalization in Python applications.
This library focuses on simplicity and predictability, avoiding complex grammar rules or plural forms.

Key features include:
- Simple translation with fallback support
- Template variable substitution using Python's string.Template
- Configuration management using pydantic-settings-manager
- Support for loading catalog from YAML file
- Cached translator instances for performance
- Type-safe with full type hints

For applications requiring advanced features like plural forms or complex localization, consider using established tools like `gettext`.
