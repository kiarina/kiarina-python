# kiarina-python

[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/badge/uv-latest-green.svg)](https://github.com/astral-sh/uv)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![CI](https://github.com/kiarina/kiarina-python/workflows/CI/badge.svg)](https://github.com/kiarina/kiarina-python/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/kiarina/kiarina-python/graph/badge.svg?token=NS6QHOXDC0)](https://codecov.io/gh/kiarina/kiarina-python)

> 🐍 **kiarina's Python utility collection** - A comprehensive namespace package monorepo providing essential utilities for modern Python development.

## 🌟 Overview

`kiarina-python` is a collection of high-quality Python utilities organized as namespace packages under the `kiarina.*` namespace.
Built with modern Python practices and managed as a monorepo using [uv workspace](https://docs.astral.sh/uv/concepts/workspaces/),
this project provides robust, well-tested utilities for common development tasks.

## 📦 Packages

### 📦 Meta Package

- **[kiarina](packages/kiarina/)** - Meta package for convenient installation
  - Install all kiarina packages with a single command: `pip install kiarina`
  - Aggregates all utilities and libraries in one package

### 🔧 Utilities

- **[kiarina-utils-common](packages/kiarina-utils-common/)** - Common utilities and helper functions
  - Configuration string parsing with nested keys and array indices
  - Type-safe utilities built with Pydantic
- **[kiarina-utils-file](packages/kiarina-utils-file/)** - Advanced file I/O operations
  - Smart encoding detection with nkf support
  - MIME type detection and FileBlob containers
  - Markdown file support with YAML front matter parsing
  - Sync & async API support with atomic operations

### 🤖 AI & LLM

- **[kiarina-llm](packages/kiarina-llm/)** - LLM integration utilities
  - LLM client abstractions and prompt management
  - Response processing helpers
  - Content measurement utilities for LLM-handled content

### 🗄️ Database Libraries

- **[kiarina-lib-falkordb](packages/kiarina-lib-falkordb/)** - FalkorDB integration
  - Configuration-based connection management
  - Thin wrapper for FalkorDB operations
- **[kiarina-lib-redis](packages/kiarina-lib-redis/)** - Redis integration
  - Configuration-based Redis client setup
  - Connection pooling and management utilities
- **[kiarina-lib-redisearch](packages/kiarina-lib-redisearch/)** - RediSearch integration
  - Search schema management and query builders
  - Full-text search utilities for Redis

### ☁️ Cloud Services

#### Cloudflare

- **[kiarina-lib-cloudflare-auth](packages/kiarina-lib-cloudflare-auth/)** - Cloudflare authentication
  - Secure credential management with SecretStr
  - Multi-configuration support for different accounts
  - Environment variable configuration
- **[kiarina-lib-cloudflare-d1](packages/kiarina-lib-cloudflare-d1/)** - Cloudflare D1 database
  - Configuration-based D1 client setup
  - Thin wrapper for Cloudflare D1 operations
  - Separation of authentication and resource configuration

#### Google Cloud

- **[kiarina-lib-google-auth](packages/kiarina-lib-google-auth/)** - Google Cloud authentication
  - Multiple authentication methods (service account, user account, default credentials)
  - Service account impersonation support
  - Credentials caching and self-signed JWT generation
- **[kiarina-lib-google-cloud-storage](packages/kiarina-lib-google-cloud-storage/)** - Google Cloud Storage
  - Configuration-based GCS client setup
  - Blob name pattern support with template placeholders
  - Multi-tenancy patterns for integration testing
  - Separation of authentication and storage configuration

## 🚀 Quick Start

### Installation

Install all packages at once with the meta package:

```bash
# Install everything
pip install kiarina

# Or with uv
uv add kiarina
```

Or install individual packages as needed:

```bash
# Core utilities
pip install kiarina-utils-common kiarina-utils-file

# LLM utilities
pip install kiarina-llm

# Database libraries
pip install kiarina-lib-redis kiarina-lib-falkordb kiarina-lib-redisearch

# Cloud services - Cloudflare
pip install kiarina-lib-cloudflare-auth kiarina-lib-cloudflare-d1

# Cloud services - Google Cloud
pip install kiarina-lib-google-auth kiarina-lib-google-cloud-storage

# Or with uv
uv add kiarina-utils-common kiarina-utils-file
```

### Basic Usage

```python
# Configuration parsing
from kiarina.utils.common import parse_config_string
config = parse_config_string("app.debug:true,db.port:5432")

# File operations with encoding detection
import kiarina.utils.file as kf
blob = kf.read_file("document.txt")  # Auto-detects encoding
data = kf.read_json_dict("config.json", default={})

# Async file operations
import kiarina.utils.file.asyncio as kfa
blob = await kfa.read_file("large_file.dat")
```

## 🏗️ Development

This project uses a modern Python development stack with [uv workspace](https://docs.astral.sh/uv/concepts/workspaces/) for monorepo management and [mise](https://mise.jdx.dev/) for task automation.

### Prerequisites

- **Python 3.12+**
- **[uv](https://github.com/astral-sh/uv)** - Fast Python package manager
- **[mise](https://mise.jdx.dev/)** - Development environment manager
- **Docker & Docker Compose** - For database testing (FalkorDB, Redis)

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/kiarina/kiarina-python.git
cd kiarina-python

# Setup development environment (installs tools, syncs dependencies, downloads test data)
mise run setup

# Verify everything works
mise run ci
```

### Development Workflow

The project uses [mise File Tasks](https://mise.jdx.dev/tasks/file-tasks.html) for all development operations:

#### All Packages

```bash
# Format all packages
mise run format

# Lint all packages
mise run lint
mise run lint-fix  # Auto-fix issues

# Type check all packages
mise run typecheck

# Test all packages (starts Docker services automatically)
mise run test

# Build all packages
mise run build

# Run complete CI pipeline
mise run ci

# Clean all build artifacts
mise run clean
```

#### Individual Packages

```bash
# Work with specific packages
mise run package:format kiarina-utils-file
mise run package:lint kiarina-utils-common
mise run package:test kiarina-llm
mise run package:build kiarina-lib-redis

# Test with coverage
mise run package:test kiarina-utils-file --coverage

# Publish to PyPI
mise run package:publish kiarina-utils-common
mise run package:publish kiarina-lib-redis --test  # Test PyPI
```

#### Utility Tasks

```bash
# Download test data for large file testing
mise run download-test-data

# Setup development environment from scratch
mise run setup

# Upgrade dependencies
mise run upgrade          # Update uv.lock only
mise run upgrade --sync   # Update and sync environment
```

### Project Structure

```
kiarina-python/
├── .github/                    # GitHub Actions workflows
├── docs/                       # Documentation (knowledges, playbooks, runbooks)
├── mise-tasks/                 # Development task definitions
├── packages/                   # Individual packages
│   ├── kiarina/                      # Meta package
│   ├── kiarina-utils-common/         # Common utilities
│   ├── kiarina-utils-file/           # File operations
│   ├── kiarina-llm/                  # LLM utilities
│   ├── kiarina-lib-falkordb/         # FalkorDB integration
│   ├── kiarina-lib-redis/            # Redis integration
│   ├── kiarina-lib-redisearch/       # RediSearch integration
│   ├── kiarina-lib-cloudflare-auth/  # Cloudflare authentication
│   ├── kiarina-lib-cloudflare-d1/    # Cloudflare D1 database
│   ├── kiarina-lib-google-auth/      # Google Cloud authentication
│   └── kiarina-lib-google-cloud-storage/  # Google Cloud Storage
├── pyproject.toml             # Workspace configuration
├── uv.lock                    # Dependency lock file
├── docker-compose.yml         # Test services (Redis, FalkorDB)
└── README.md                  # This file
```

### Technology Stack

- **Language**: Python 3.12+
- **Package Management**: [uv](https://github.com/astral-sh/uv) with workspace support
- **Task Runner**: [mise](https://mise.jdx.dev/) File Tasks
- **Code Formatting**: [ruff](https://github.com/astral-sh/ruff)
- **Linting**: [ruff](https://github.com/astral-sh/ruff)
- **Type Checking**: [mypy](https://mypy.readthedocs.io/)
- **Testing**: [pytest](https://pytest.org/) with asyncio support
- **CI/CD**: GitHub Actions
- **Repository Style**: Monorepo with uv workspace

### uv Workspace Configuration

This project leverages [uv workspace](https://docs.astral.sh/uv/concepts/workspaces/) for efficient monorepo management:

- **Shared dependencies**: Common dev/test dependencies managed at the root level
- **Editable installs**: All packages automatically installed in editable mode
- **Unified lockfile**: Single `uv.lock` for consistent dependency resolution
- **Cross-package dependencies**: Packages can depend on each other seamlessly

Key workspace features:
- `uv sync --all-packages` - Sync all workspace packages
- `uv build --all` - Build all packages
- Automatic editable installation of workspace packages
- Shared virtual environment with isolated package sources

### Testing

The project includes comprehensive testing with special considerations:

- **Docker services**: Tests requiring Redis/FalkorDB automatically start services
- **Large test data**: Downloaded from [kiarina/test-data](https://github.com/kiarina/test-data) releases
- **Async testing**: Full support for async/await patterns
- **Coverage reporting**: Available per package or across the workspace

Test data organization:
- `tests/fixtures/` - Small JSON/YAML files for fixtures
- `tests/data/small/` - Small test files (< 1MB)
- `tests/data/large/` - Large test files (downloaded separately)

### CI/CD Pipeline

Automated workflows using GitHub Actions:

- **CI**: Format, lint, type check, test, and build on every PR/push
- **Release**: Automatic releases on version tags
- **Dependency Updates**: Weekly automated dependency updates
- **Security Audit**: Daily security vulnerability scanning

## 🤝 Contributing

This is primarily a personal project, but contributions are welcome! 🙂

### How to Contribute

- **Issues**: Feel free to open issues for bugs or feature requests
- **Pull Requests**: PRs are welcome, though response time may vary as this is a side project
- **Discussions**: Use GitHub Discussions for questions or general discussion

### Development Guidelines

- Follow the existing code style (enforced by ruff)
- Add tests for new functionality
- Update documentation as needed
- Run `mise run ci` before submitting PRs

No formal contribution guidelines - just make sure tests pass and code is reasonably formatted.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[uv](https://github.com/astral-sh/uv)**: Modern Python package management and workspace support
- **[mise](https://mise.jdx.dev/)**: Development environment and task management
- **[ruff](https://github.com/astral-sh/ruff)**: Fast Python linter and formatter
- **[Pydantic](https://pydantic.dev/)**: Data validation and settings management

---

<div align="center">

**Made with ❤️ by [kiarina](https://github.com/kiarina)**

*Building better Python utilities, one package at a time.*

</div>
