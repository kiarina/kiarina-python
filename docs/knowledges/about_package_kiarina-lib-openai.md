---
title: About kiarina-lib-openai package
description: >-
  kiarina-lib-openai is a library for OpenAI API integration
  with configuration management using pydantic-settings-manager.
---

kiarina-lib-openai provides a simple and secure way to manage OpenAI API credentials using pydantic-settings-manager.
This library enables the implementation of OpenAI-related functionality by separating and managing API credentials from the application.

Key features include:
- Secure API key management with SecretStr
- Multi-configuration support for different projects/environments
- Custom base URL support for OpenAI-compatible APIs (e.g., Azure OpenAI, local models)
- Organization ID support
- Environment variable configuration
