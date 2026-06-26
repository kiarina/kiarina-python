# kiarina-python

English | [日本語](README.ja.md)

[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/badge/uv-latest-green.svg)](https://github.com/astral-sh/uv)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![CI](https://github.com/kiarina/kiarina-python/workflows/CI/badge.svg)](https://github.com/kiarina/kiarina-python/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/kiarina/kiarina-python/graph/badge.svg?token=NS6QHOXDC0)](https://codecov.io/gh/kiarina/kiarina-python)

> 🚀 **kiarina-python** - A foundational collection of Python modules for building LLM agents with qualia (the subjective texture of consciousness).

## 🌟 Overview

`kiarina-python` is a collection of foundational modules designed to build advanced AI systems, specifically "LLM agents with qualia."

Rather than just a set of generic utilities, it serves as the underlying framework supporting autonomous LLM reasoning, persistent memory (FalkorDB, Redis), and interaction with the external environment (file operations, various cloud/AI API integrations).

## 🏗️ Design Philosophy

- **Monorepo Structure**: All modules are organized as `kiarina.*` namespace packages and robustly managed using modern Python practices and [uv workspace](https://docs.astral.sh/uv/concepts/workspaces/).
- **Crystal Architecture**: This project adopts the [Crystal Architecture](https://github.com/kiarina/crystal-architecture), ensuring a highly modular, maintainable, and scalable codebase.
- **Configuration Injection**: By utilizing [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager), the declaration of configuration dependencies is localized within each module, while still allowing for unified global management when the system is integrated.

## 📦 Packages

### 📦 Meta Package

- **[kiarina](packages/kiarina/)** - Meta package for convenient installation
  - Install all kiarina packages with a single command: `pip install kiarina`
  - Aggregates all utilities and libraries in one package

### 🌍 Internationalization & Localization

- **[kiarina-i18n](packages/kiarina-i18n/)** - Simple internationalization (i18n) utilities
  - Lightweight translation with fallback support
  - Template variable substitution
  - Configuration-based catalog management
  - YAML file support for translations
- **[kiarina-currency](packages/kiarina-currency/)** - Currency utilities with exchange rate support
  - System currency detection from locale settings
  - Exchange rate retrieval with pluggable rate providers
  - Static and real-time (Frankfurter API) rate providers
  - ISO 4217 currency code support

### 🔧 Utilities

- **[kiarina-utils-common](packages/kiarina-utils-common/)** - Common utilities and helper functions
  - Configuration string parsing with nested keys and array indices
  - Type-safe utilities built with Pydantic
- **[kiarina-utils-file](packages/kiarina-utils-file/)** - Advanced file I/O operations
  - Smart encoding detection with nkf support
  - MIME type detection and FileBlob containers
  - Markdown file support with YAML front matter parsing
  - Sync & async API support with atomic operations

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

- **[kiarina-lib-anthropic](packages/kiarina-lib-anthropic/)** - Anthropic API integration
  - Secure API key management with SecretStr
  - Multi-configuration support for different projects/environments
  - Custom base URL support for Anthropic-compatible APIs
  - Environment variable configuration
- **[kiarina-lib-cloudflare](packages/kiarina-lib-cloudflare/)** - Cloudflare authentication
  - Secure credential management with SecretStr
  - Multi-configuration support for different accounts
  - Environment variable configuration
- **[kiarina-lib-cloudflare-d1](packages/kiarina-lib-cloudflare-d1/)** - Cloudflare D1 database
  - Configuration-based D1 client setup
  - Thin wrapper for Cloudflare D1 operations
  - Separation of authentication and resource configuration
- **[kiarina-lib-firebase](packages/kiarina-lib-firebase/)** - Firebase authentication
  - Custom token exchange for refresh/ID tokens via REST API
  - Automatic ID token lifecycle management with TokenManager
  - Token refresh 5 minutes before expiration
  - Thread-safe token refresh with asyncio.Lock
  - Secure API key management with SecretStr
- **[kiarina-lib-firebase-rtdb](packages/kiarina-lib-firebase-rtdb/)** - Firebase Realtime Database
  - Real-time state synchronization and data persistence for agents
  - Lightweight REST API-based client using HTTPX
- **[kiarina-lib-google](packages/kiarina-lib-google/)** - Google Cloud authentication
  - Multiple authentication methods (service account, user account, default credentials)
  - Service account impersonation support
  - Credentials caching and self-signed JWT generation
- **[kiarina-lib-openai](packages/kiarina-lib-openai/)** - OpenAI API integration
  - Secure API key management with SecretStr
  - Multi-configuration support for different projects/environments
  - Custom base URL support for OpenAI-compatible APIs
  - Environment variable configuration
- **[kiarina-lib-slack](packages/kiarina-lib-slack/)** - Slack API client
  - Interface for dialogue between the agent and human users
  - Configuration-based secure Bot token management

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
pip install kiarina-i18n kiarina-utils-common kiarina-utils-file

# Database libraries
pip install kiarina-lib-redis kiarina-lib-falkordb kiarina-lib-redisearch

# Cloud services - AI Services
pip install kiarina-lib-anthropic kiarina-lib-openai

# Cloud services - Cloudflare
pip install kiarina-lib-cloudflare kiarina-lib-cloudflare-d1

# Cloud services - Firebase
pip install kiarina-lib-firebase kiarina-lib-firebase-rtdb

# Cloud services - Google Cloud
pip install kiarina-lib-google

# Cloud services - Slack
pip install kiarina-lib-slack

# Or with uv
uv add kiarina-utils-common kiarina-utils-file
```


## 🏗️ Development

This project uses a modern Python development stack with [uv workspace](https://docs.astral.sh/uv/concepts/workspaces/) for monorepo management and [mise](https://mise.jdx.dev/) for task automation.

### Prerequisites

- **Python 3.12+**
- **[uv](https://github.com/astral-sh/uv)** - Fast Python package manager
- **[mise](https://mise.jdx.dev/)** - Development environment manager
- **Docker & Docker Compose** - For database testing (FalkorDB, Redis)
- **[age](https://age-encryption.org/)** - Encryption for shared test settings
- **[Google Cloud CLI](https://cloud.google.com/sdk/docs/install)** - Access to the private test settings bucket

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

Use Makefile shortcuts for common all-package workflows:

```bash
# Format all packages (auto-fixes lint issues)
make format

# Lint and type check all packages
make lint

# Test all packages (starts Docker services automatically)
make test

# Build all packages
make build

# Run complete CI pipeline
make ci

# Clean all build artifacts
make clean
```

The Makefile shortcuts run the underlying mise tasks (`mise run format`, `mise run test`, `mise run build`, …) without a package argument, which targets every package.

#### Individual Packages

Every task accepts an optional package name. Without one, it targets the package of the current directory (or all packages at the repository root):

```bash
# Work with specific packages
mise run format kiarina-utils-file
mise run lint kiarina-utils-common
mise run build kiarina-lib-redis

# Test with coverage
mise run test kiarina-utils-file --coverage

# Publish to PyPI
mise run publish kiarina-utils-common
mise run publish kiarina-lib-redis --test  # Test PyPI

# Or cd into a package and omit the name; each package has its own Makefile
cd packages/kiarina-utils-file
make format      # equivalent to: mise run format kiarina-utils-file
make check       # format + lint + test with coverage
```

#### Utility Tasks

```bash
# Setup development environment from scratch
mise run setup

# Sync dependencies and show outdated packages
make update

# Upgrade dependencies and sync the environment
make upgrade
```

#### Test Settings

Ignored `.env` and `test_settings.yaml` files can be encrypted with age and shared through a private Google Cloud Storage prefix.

See the [Test Settings runbook](docs/runbooks/test_settings/README.md) for age key generation, bucket creation, IAM configuration, environment setup, daily operation, and key rotation.

Set the following variables in your shell or another secret store. Do not put the age identity in a repository `.env` file because `.env` is itself managed by these tasks.

```bash
export KIARINA_TEST_SETTINGS_GCS_URI="gs://your-private-bucket/kiarina-python"
export KIARINA_TEST_SETTINGS_AGE_RECIPIENT="age1..."
export KIARINA_TEST_SETTINGS_AGE_IDENTITY="AGE-SECRET-KEY-1..."
```

Upload every ignored `.env` and `test_settings.yaml` file:

```bash
mise run test-settings:upload --dry-run
mise run test-settings:upload
```

Download and decrypt all managed files. Existing files are preserved unless `--force` is specified.

```bash
mise run test-settings:download --dry-run
mise run test-settings:download
mise run test-settings:download --force
```

The upload task uses only the age recipient. The download task requires the age identity, writes files atomically, and sets their permissions to `0600`. Upload never deletes remote objects automatically.

### Project Structure

```
kiarina-python/
├── .github/                    # GitHub Actions workflows
├── .mise/tasks/                # Development task definitions
├── docs/                       # Documentation (concepts, playbooks, runbooks)
├── packages/                   # Individual packages
│   ├── kiarina/                      # Meta package
│   ├── kiarina-utils-common/         # Common utilities
│   ├── kiarina-utils-file/           # File operations
│   ├── kiarina-lib-falkordb/         # FalkorDB integration
│   ├── kiarina-lib-redis/            # Redis integration
│   ├── kiarina-lib-redisearch/       # RediSearch integration
│   ├── kiarina-lib-anthropic/        # Anthropic API integration
│   ├── kiarina-lib-cloudflare/       # Cloudflare authentication
│   ├── kiarina-lib-cloudflare-d1/    # Cloudflare D1 database
│   ├── kiarina-lib-firebase/         # Firebase authentication
│   ├── kiarina-lib-firebase-rtdb/    # Firebase Realtime Database
│   ├── kiarina-lib-google/           # Google Cloud authentication
│   ├── kiarina-lib-openai/           # OpenAI API integration
│   ├── kiarina-lib-slack/            # Slack API client
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
- `tests/assets/` - Sample files used in tests

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

**Programming is Elegant.**

</div>
