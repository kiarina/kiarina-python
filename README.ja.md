# kiarina-python

[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/kiarina/kiarina-python/actions/workflows/ci.yml/badge.svg)](https://github.com/kiarina/kiarina-python/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/kiarina/kiarina-python/graph/badge.svg?token=NS6QHOXDC0)](https://codecov.io/gh/kiarina/kiarina-python)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

[English](README.md) | 日本語

> [!NOTE] これは何？
> `kiarina-python` は、Python アプリケーションや LLM エージェントの開発で使用するパッケージを管理するモノレポです。
>
> 各パッケージは `kiarina.*` namespace の一部として提供され、必要なものだけを個別にインストールできます。すべてのパッケージをまとめたメタパッケージも用意しています。

## Packages

### Meta Package

| Package | Description |
| --- | --- |
| [kiarina](packages/kiarina/) | このリポジトリの全パッケージをまとめてインストールするメタパッケージ |

### Application Utilities

| Package | Description |
| --- | --- |
| [kiarina-utils-app](packages/kiarina-utils-app/) | アプリケーション設定、ユーザーディレクトリ、重複起動制御 |
| [kiarina-utils-common](packages/kiarina-utils-common/) | 設定解決、動的 import、component registry |
| [kiarina-utils-file](packages/kiarina-utils-file/) | 同期・非同期の file I/O、encoding、MIME type、拡張子の検出 |
| [kiarina-i18n](packages/kiarina-i18n/) | dictionary と YAML catalog を使用する国際化 |
| [kiarina-currency](packages/kiarina-currency/) | システム通貨の検出と為替レートの取得 |

### AI Agents

| Package | Description |
| --- | --- |
| [kiarina-agi-audio](packages/kiarina-agi-audio/) | AI agent 向けの audio source、speech、tagging、embedding、voice activity |
| [kiarina-agi-base](packages/kiarina-agi-base/) | AI agent 向けの context、cost・request logging、recording、token utility |
| [kiarina-agi-data](packages/kiarina-agi-data/) | AI agent 向けの message、event、embedding、file metadata などの data model |
| [kiarina-agi-data-builder](packages/kiarina-agi-data-builder/) | AI agent 向けの message、event、history、tool、file、file segment builder |
| [kiarina-agi-file](packages/kiarina-agi-file/) | AI agent 向けの local・cloud asset repository、cache、file resolution |
| [kiarina-agi-flow](packages/kiarina-agi-flow/) | AI agent 向けの prompt、section、state、workflow orchestration |
| [kiarina-agi-image](packages/kiarina-agi-image/) | AI agent 向けの image detection、embedding、generation |
| [kiarina-agi-runner](packages/kiarina-agi-runner/) | AI agent 向けの agent 実行、task runner、structured output helper |
| [kiarina-agi-text](packages/kiarina-agi-text/) | AI agent 向けの chat、logging、text embedding |
| [kiarina-agi-tool](packages/kiarina-agi-tool/) | AI agent 向けの tool 実行、hook、tool logging |
| [kiarina-agi-video](packages/kiarina-agi-video/) | AI agent 向けの video source と video generation |

### Data Stores

| Package | Description |
| --- | --- |
| [kiarina-lib-falkordb](packages/kiarina-lib-falkordb/) | FalkorDB の同期・非同期 client と接続管理 |
| [kiarina-lib-redis](packages/kiarina-lib-redis/) | Redis の同期・非同期 client と接続管理 |
| [kiarina-lib-redisearch](packages/kiarina-lib-redisearch/) | RediSearch の client、検索 filter、index schema |

### External Services

| Package | Description |
| --- | --- |
| [kiarina-lib-anthropic](packages/kiarina-lib-anthropic/) | Anthropic API の接続設定 |
| [kiarina-lib-cloudflare](packages/kiarina-lib-cloudflare/) | Cloudflare account の認証設定 |
| [kiarina-lib-cloudflare-d1](packages/kiarina-lib-cloudflare-d1/) | Cloudflare D1 REST API の同期・非同期 client |
| [kiarina-lib-firebase](packages/kiarina-lib-firebase/) | Firebase Authentication の token 管理 |
| [kiarina-lib-firebase-rtdb](packages/kiarina-lib-firebase-rtdb/) | Firebase Realtime Database の REST client |
| [kiarina-lib-google](packages/kiarina-lib-google/) | Google Cloud の認証設定と credentials 管理 |
| [kiarina-lib-openai](packages/kiarina-lib-openai/) | OpenAI API の接続設定 |
| [kiarina-lib-slack](packages/kiarina-lib-slack/) | Slack app の認証設定 |

各パッケージの install 方法と公開 API は、リンク先の README を参照してください。

## Installation

Python 3.12 以降が必要です。

すべてのパッケージをインストールする場合:

```bash
pip install kiarina
```

必要なパッケージだけをインストールする場合:

```bash
pip install kiarina-utils-file kiarina-lib-redis
```

uv でも同様に追加できます。

```bash
uv add kiarina-utils-file kiarina-lib-redis
```

## Design

- パッケージは `kiarina.*` namespace を共有し、独立して配布します。
- リポジトリは [uv workspace](https://docs.astral.sh/uv/concepts/workspaces/) で管理します。
- モジュール間の依存関係は [Crystal Architecture](https://github.com/kiarina/crystal-architecture) に沿って整理します。
- 設定を扱うパッケージでは、主に [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) を使用します。

## Development

### Requirements

- Python 3.12 以降
- [uv](https://docs.astral.sh/uv/)
- [mise](https://mise.jdx.dev/)
- Docker と Docker Compose

一部の test settings を取得する場合は、[age](https://age-encryption.org/) と [Google Cloud CLI](https://cloud.google.com/sdk/docs/install) も必要です。

### Setup

```bash
git clone https://github.com/kiarina/kiarina-python.git
cd kiarina-python
mise run setup
```

`mise run setup` は tool と依存関係を準備し、共有 test assets をダウンロードします。

### Common Tasks

リポジトリ全体に対して実行する場合:

```bash
make format
make lint
make test
make build
make ci
```

特定のパッケージに対して実行する場合:

```bash
mise run format kiarina-utils-file
mise run lint kiarina-utils-file
mise run test kiarina-utils-file
mise run build kiarina-utils-file
```

パッケージで pytest を設定する場合は、pytest の引数を `packages/<package>/tests/.pytest-args` に記述します。

```text
-n 8 --timeout 120 --reruns 3 --reruns-delay 5
```

各パッケージのディレクトリでは、そのパッケージの `Makefile` も使用できます。

```bash
cd packages/kiarina-utils-file
make check
```

### Test Assets and Settings

共有 test assets は [kiarina/test-assets](https://github.com/kiarina/test-assets) で管理しています。

```bash
mise run test-assets:download
```

gitignore された `.env` と `test_settings.yaml` は、age で暗号化して private な Google Cloud Storage prefix で共有できます。設定方法は [kiarina/test-settings](https://github.com/kiarina/test-settings) を参照してください。

## Documentation

- [Development Flow](docs/playbooks/development_flow/README.ja.md)
- [Implementation Optional Dependencies](docs/concepts/implementation_optional_dependencies/README.ja.md)
- [uv Workspace Operations](docs/concepts/uv_workspace_operations/README.ja.md)
- [Sensitive Data Security](docs/concepts/sensitive_data_security/README.ja.md)
- [Adding a Package](docs/runbooks/add_new_package/README.ja.md)
- [Release](docs/runbooks/release/README.ja.md)

## Contributing

Issue と Pull Request を受け付けています。変更を送る前に `make` と対象パッケージの test を実行してください。

```bash
make
mise run test <package_name>
```

## License

[MIT License](LICENSE)
