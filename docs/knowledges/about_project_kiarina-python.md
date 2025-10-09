---
title: About This Project (kiarina-python)
description: >-
  kiarina-python is an OSS Python package developed personally by kiarina.
  Namespace packages under `kiarina` namespace are managed in a monorepo using uv workspace.
---

## What is the kiarina-python Project?

An OSS Python package developed personally by kiarina.
While it's open source, this is a personal project where I want creative freedom,
so while Issues and Pull Requests are appreciated, they're not actively solicited.
Packages under the `kiarina` namespace will be published to PyPI as kiarina-* packages.

## Provided Packages

- kiarina: Meta package for the `kiarina` namespace
- kiarina-lib-cloudflare-auth: `kiarina.lib.cloudflare.auth` package. Cloudflare authentication utilities
- kiarina-lib-falkordb: `kiarina.lib.falkordb` package. FalkorDB utilities
- kiarina-lib-google-auth: `kiarina.lib.google.auth` package. Google Cloud authentication utilities
- kiarina-lib-redis: `kiarina.lib.redis` package. Redis utilities
- kiarina-lib-redisearch: `kiarina.lib.redisearch` package. Advanced Redisearch wrapper
- kiarina-llm: `kiarina.llm` package. LLM utilities
- kiarina-utils-common: `kiarina.utils.common` package. Common utilities
- kiarina-utils-file: `kiarina.utils.file` package. File operation utilities

## Tech Stack

- language: Python 3.12+
- runtime management: mise
- dependency / environment management: uv
- repository style: monorepo + uv workspace
- code formatting: ruff
- linting: ruff
- typecheck: mypy
- testing: pytest
- task runner: mise (File Tasks)
