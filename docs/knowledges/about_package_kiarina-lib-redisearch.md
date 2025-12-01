---
title: About kiarina-lib-redisearch package
description: >-
  kiarina-lib-redisearch is a comprehensive library for RediSearch
  with advanced configuration management, schema definition, and both full-text and vector search capabilities.
---

kiarina-lib-redisearch is a comprehensive wrapper library for using RediSearch with Python.
The purpose of this library is to provide type-safe schema definition, advanced filtering, and complete index lifecycle management while separating infrastructure settings from the application.

Key features include:
- Full-text search with stemming, phonetic matching, and fuzzy search
- Vector search using FLAT and HNSW algorithms
- Type-safe schema definition with automatic migration support
- Configuration management using pydantic-settings-manager
- Sync & Async API support
- Advanced filtering with intuitive query builder
- Index management (create, migrate, reset, drop)

When running tests, please start Redis with RediSearch module using `docker compose up -d redis` before execution.
