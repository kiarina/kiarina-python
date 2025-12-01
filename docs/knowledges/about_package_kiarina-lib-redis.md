---
title: About kiarina-lib-redis package
description: >-
  kiarina-lib-redis is a library for Redis client management
  with configuration management using pydantic-settings-manager.
---

kiarina-lib-redis is a thin wrapper library for using Redis with Python.
The purpose of this library is to completely separate infrastructure settings such as connection information and retry configuration from the application.

Key features include:
- Configuration-based Redis client setup
- Connection pooling and caching
- Retry mechanism for connection failures
- Sync & Async API support
- Environment variable configuration

When running tests, please start Redis with `docker compose up -d redis` before execution.
