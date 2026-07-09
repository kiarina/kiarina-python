# kiarina-python

[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/kiarina/kiarina-python/actions/workflows/ci.yml/badge.svg)](https://github.com/kiarina/kiarina-python/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/kiarina/kiarina-python/graph/badge.svg?token=NS6QHOXDC0)](https://codecov.io/gh/kiarina/kiarina-python)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

English | [日本語](README.ja.md)

> [!NOTE] What is this?
> `kiarina-python` is a monorepo for packages used to build Python applications and LLM agents.
>
> Each package is distributed as part of the `kiarina.*` namespace and can be installed independently. A meta package is also available to install the complete collection.

## Packages

### Meta Package

| Package | Description |
| --- | --- |
| [kiarina](packages/kiarina/) | Meta package that installs every package in this repository |

### Application Utilities

| Package | Description |
| --- | --- |
| [kiarina-utils-app](packages/kiarina-utils-app/) | Application configuration, user directories, and single-instance control |
| [kiarina-utils-common](packages/kiarina-utils-common/) | Configuration resolution, dynamic imports, and component registries |
| [kiarina-utils-file](packages/kiarina-utils-file/) | Synchronous and asynchronous file I/O and encoding, MIME type, and extension detection |
| [kiarina-i18n](packages/kiarina-i18n/) | Internationalization using dictionary and YAML catalogs |
| [kiarina-currency](packages/kiarina-currency/) | System currency detection and exchange rate retrieval |

### AI Agents

| Package | Description |
| --- | --- |
| [kiarina-agi-audio](packages/kiarina-agi-audio/) | Audio sources, speech, tagging, embeddings, and voice activity for AI agents |
| [kiarina-agi-base](packages/kiarina-agi-base/) | Core contexts, cost and request logging, recording, and token utilities for AI agents |
| [kiarina-agi-data](packages/kiarina-agi-data/) | Messages, events, embeddings, file metadata, and other data models for AI agents |
| [kiarina-agi-data-builder](packages/kiarina-agi-data-builder/) | Builders for AI agent messages, events, histories, tools, files, and file segments |
| [kiarina-agi-file](packages/kiarina-agi-file/) | Local and cloud asset repositories, caching, and file resolution for AI agents |
| [kiarina-agi-flow](packages/kiarina-agi-flow/) | Prompt, section, state, and workflow orchestration for AI agents |
| [kiarina-agi-image](packages/kiarina-agi-image/) | Image detection, embedding, and generation for AI agents |
| [kiarina-agi-text](packages/kiarina-agi-text/) | Chat, logging, and text embeddings for AI agents |
| [kiarina-agi-tool](packages/kiarina-agi-tool/) | Tool execution, hooks, and tool logging for AI agents |
| [kiarina-agi-video](packages/kiarina-agi-video/) | Video sources and video generation for AI agents |

### Data Stores

| Package | Description |
| --- | --- |
| [kiarina-lib-falkordb](packages/kiarina-lib-falkordb/) | Synchronous and asynchronous FalkorDB clients and connection management |
| [kiarina-lib-redis](packages/kiarina-lib-redis/) | Synchronous and asynchronous Redis clients and connection management |
| [kiarina-lib-redisearch](packages/kiarina-lib-redisearch/) | RediSearch clients, search filters, and index schemas |

### External Services

| Package | Description |
| --- | --- |
| [kiarina-lib-anthropic](packages/kiarina-lib-anthropic/) | Anthropic API connection settings |
| [kiarina-lib-cloudflare](packages/kiarina-lib-cloudflare/) | Cloudflare account authentication settings |
| [kiarina-lib-cloudflare-d1](packages/kiarina-lib-cloudflare-d1/) | Synchronous and asynchronous clients for the Cloudflare D1 REST API |
| [kiarina-lib-firebase](packages/kiarina-lib-firebase/) | Firebase Authentication token management |
| [kiarina-lib-firebase-rtdb](packages/kiarina-lib-firebase-rtdb/) | REST client for Firebase Realtime Database |
| [kiarina-lib-google](packages/kiarina-lib-google/) | Google Cloud authentication settings and credential management |
| [kiarina-lib-openai](packages/kiarina-lib-openai/) | OpenAI API connection settings |
| [kiarina-lib-slack](packages/kiarina-lib-slack/) | Slack app authentication settings |

See each package README for installation instructions and its public API.

## Installation

Python 3.12 or later is required.

To install every package:

```bash
pip install kiarina
```

To install only the packages you need:

```bash
pip install kiarina-utils-file kiarina-lib-redis
```

The same packages can be added with uv:

```bash
uv add kiarina-utils-file kiarina-lib-redis
```

## Design

- Packages share the `kiarina.*` namespace and are distributed independently.
- The repository is managed as an [uv workspace](https://docs.astral.sh/uv/concepts/workspaces/).
- Dependencies between modules are organized according to [Crystal Architecture](https://github.com/kiarina/crystal-architecture).
- Packages that require configuration primarily use [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager).

## Development

### Requirements

- Python 3.12 or later
- [uv](https://docs.astral.sh/uv/)
- [mise](https://mise.jdx.dev/)
- Docker and Docker Compose

[age](https://age-encryption.org/) and the [Google Cloud CLI](https://cloud.google.com/sdk/docs/install) are also required to retrieve some test settings.

### Setup

```bash
git clone https://github.com/kiarina/kiarina-python.git
cd kiarina-python
mise run setup
```

`mise run setup` prepares the tools and dependencies and downloads the shared test assets.

### Common Tasks

To run tasks across the repository:

```bash
make format
make lint
make test
make build
make ci
```

To run tasks for a specific package:

```bash
mise run format kiarina-utils-file
mise run lint kiarina-utils-file
mise run test kiarina-utils-file
mise run build kiarina-utils-file
```

To configure pytest for a package, add its arguments to `packages/<package>/tests/.pytest-args`.

```text
-n 8 --timeout 120 --reruns 3 --reruns-delay 5
```

Each package directory also contains a `Makefile` for that package.

```bash
cd packages/kiarina-utils-file
make check
```

### Test Assets and Settings

Shared test assets are maintained in [kiarina/test-assets](https://github.com/kiarina/test-assets).

```bash
mise run test-assets:download
```

Git-ignored `.env` and `test_settings.yaml` files can be encrypted with age and shared through a private Google Cloud Storage prefix. See [kiarina/test-settings](https://github.com/kiarina/test-settings) for configuration details.

## Documentation

- [Development Flow](docs/playbooks/development_flow/README.md)
- [Implementation Optional Dependencies](docs/concepts/implementation_optional_dependencies/README.md)
- [uv Workspace Operations](docs/concepts/uv_workspace_operations/README.md)
- [Sensitive Data Security](docs/concepts/sensitive_data_security/README.md)
- [Adding a Package](docs/runbooks/add_new_package/README.md)
- [Release](docs/runbooks/release/README.md)

## Contributing

Issues and pull requests are welcome. Before submitting a change, run `make` and the tests for the affected package.

```bash
make
mise run test <package_name>
```

## License

[MIT License](LICENSE)
