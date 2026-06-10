# kiarina-python

[English](README.md) | [日本語](README.ja.md)

[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/badge/uv-latest-green.svg)](https://github.com/astral-sh/uv)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![CI](https://github.com/kiarina/kiarina-python/workflows/CI/badge.svg)](https://github.com/kiarina/kiarina-python/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/kiarina/kiarina-python/graph/badge.svg?token=NS6QHOXDC0)](https://codecov.io/gh/kiarina/kiarina-python)

> 🚀 **kiarina-python** - クオリア（意識の質感）を持つ LLM エージェントを開発するための土台となる、包括的なPythonモジュール群。

## 🌟 概要 (Overview)

`kiarina-python` は、「クオリアを持つ LLM エージェント」という高度なAIシステムを構築するための土台となるフレームワークを構成するモジュール群です。

単なる汎用ユーティリティの集まりではなく、LLMの自律的な思考、記憶の永続化（FalkorDB, Redis）、外部環境との相互作用（ファイル操作、各種クラウド・AI API連携）を支えるための基盤として設計されています。

## 🏗️ 設計思想 (Design Philosophy)

- **モノレポ構成**: すべてのモジュールは `kiarina.*` 名前空間パッケージとして整理され、モダンなPythonのプラクティスと [uv workspace](https://docs.astral.sh/uv/concepts/workspaces/) を用いたモノレポ構成により堅牢に管理されています。
- **結晶アーキテクチャ**: 本プロジェクトは [結晶アーキテクチャ (Crystal Architecture)](https://github.com/kiarina/crystal-architecture) を採用しており、高度にモジュール化され、保守性とスケーラビリティに優れたコードベースを実現しています。
- **設定の注入 (Configuration Injection)**: [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) を活用することで、設定という依存の宣言を各モジュールに局所化しつつ、システム全体として統合した際にも一元的に管理できる仕組みを実現しています。

## 📦 パッケージ (Packages)

### 📦 メタパッケージ (Meta Package)

- **[kiarina](packages/kiarina/)** - 簡単なインストールのためのメタパッケージ
  - 1つのコマンドですべての kiarina パッケージをインストール: `pip install kiarina`
  - すべてのユーティリティとライブラリを1つのパッケージに集約

### 🌍 国際化とローカリゼーション (Internationalization & Localization)

- **[kiarina-i18n](packages/kiarina-i18n/)** - シンプルな国際化 (i18n) ユーティリティ
  - フォールバック対応の軽量な翻訳
  - テンプレート変数の置換
  - 設定ベースのカタログ管理
  - 翻訳用のYAMLファイルサポート
- **[kiarina-currency](packages/kiarina-currency/)** - 為替レート対応の通貨ユーティリティ
  - ロケール設定からのシステム通貨の検出
  - プラグイン可能なレートプロバイダーによる為替レートの取得
  - 静的およびリアルタイム (Frankfurter API) レートプロバイダー
  - ISO 4217 通貨コードのサポート

### 🔧 ユーティリティ (Utilities)

- **[kiarina-utils-common](packages/kiarina-utils-common/)** - 共通ユーティリティとヘルパー関数
  - ネストされたキーと配列インデックスを持つ設定文字列のパース
  - Pydanticで構築された型安全なユーティリティ
- **[kiarina-utils-file](packages/kiarina-utils-file/)** - 高度なファイルI/O操作
  - nkfサポートによるスマートなエンコーディング検出
  - MIMEタイプの検出とFileBlobコンテナ
  - YAMLフロントマターのパース付きMarkdownファイルのサポート
  - アトミック操作による同期および非同期APIのサポート

### 🗄️ データベースライブラリ (Database Libraries)

- **[kiarina-lib-falkordb](packages/kiarina-lib-falkordb/)** - FalkorDB 連携
  - 設定ベースの接続管理
  - FalkorDB操作のための薄いラッパー
- **[kiarina-lib-redis](packages/kiarina-lib-redis/)** - Redis 連携
  - 設定ベースのRedisクライアントセットアップ
  - 接続プーリングと管理ユーティリティ
- **[kiarina-lib-redisearch](packages/kiarina-lib-redisearch/)** - RediSearch 連携
  - 検索スキーマ管理とクエリビルダー
  - Redis用のフルテキスト検索ユーティリティ

### ☁️ クラウドサービス (Cloud Services)

- **[kiarina-lib-anthropic](packages/kiarina-lib-anthropic/)** - Anthropic API 連携
  - SecretStrを用いた安全なAPIキー管理
  - 異なるプロジェクト/環境のマルチ設定サポート
  - Anthropic互換APIのためのカスタムベースURLサポート
  - 環境変数による設定
- **[kiarina-lib-cloudflare](packages/kiarina-lib-cloudflare/)** - Cloudflare 認証
  - SecretStrを用いた安全なクレデンシャル管理
  - 異なるアカウントのマルチ設定サポート
  - 環境変数による設定
- **[kiarina-lib-cloudflare-d1](packages/kiarina-lib-cloudflare-d1/)** - Cloudflare D1 データベース
  - 設定ベースのD1クライアントセットアップ
  - Cloudflare D1 操作のための薄いラッパー
  - 認証とリソース設定の分離
- **[kiarina-lib-firebase](packages/kiarina-lib-firebase/)** - Firebase 認証
  - REST API経由の更新/IDトークンのためのカスタムトークン交換
  - TokenManagerによるIDトークンライフサイクルの自動管理
  - 有効期限5分前のトークン更新
  - asyncio.Lockを用いたスレッドセーフなトークン更新
  - SecretStrを用いた安全なAPIキー管理
- **[kiarina-lib-firebase-rtdb](packages/kiarina-lib-firebase-rtdb/)** - Firebase Realtime Database
  - エージェントのリアルタイムな状態同期やデータ保存
  - HTTPXを用いたREST APIベースの軽量なクライアント
- **[kiarina-lib-google](packages/kiarina-lib-google/)** - Google Cloud 認証
  - 複数の認証方法（サービスアカウント、ユーザーアカウント、デフォルト認証情報）
  - サービスアカウントのなりすまし（Impersonation）サポート
  - 認証情報のキャッシングと自己署名JWTの生成
- **[kiarina-lib-openai](packages/kiarina-lib-openai/)** - OpenAI API 連携
  - SecretStrを用いた安全なAPIキー管理
  - 異なるプロジェクト/環境のマルチ設定サポート
  - OpenAI互換APIのためのカスタムベースURLサポート
  - 環境変数による設定
- **[kiarina-lib-slack](packages/kiarina-lib-slack/)** - Slack API クライアント
  - エージェントと人間のユーザーが対話するためのインターフェース
  - 設定ベースのセキュアなBotトークン管理

## 🚀 クイックスタート (Quick Start)

### インストール (Installation)

メタパッケージを使用してすべてのパッケージを一度にインストールします：

```bash
# すべてインストール
pip install kiarina

# または uv を使用
uv add kiarina
```

または必要に応じて個別のパッケージをインストールします：

```bash
# コアユーティリティ
pip install kiarina-i18n kiarina-utils-common kiarina-utils-file

# データベースライブラリ
pip install kiarina-lib-redis kiarina-lib-falkordb kiarina-lib-redisearch

# クラウドサービス - AI サービス
pip install kiarina-lib-anthropic kiarina-lib-openai

# クラウドサービス - Cloudflare
pip install kiarina-lib-cloudflare kiarina-lib-cloudflare-d1

# クラウドサービス - Firebase
pip install kiarina-lib-firebase kiarina-lib-firebase-rtdb

# クラウドサービス - Google Cloud
pip install kiarina-lib-google

# クラウドサービス - Slack
pip install kiarina-lib-slack

# または uv を使用
uv add kiarina-utils-common kiarina-utils-file
```


## 🏗️ 開発 (Development)

このプロジェクトは、モノレポ管理に [uv workspace](https://docs.astral.sh/uv/concepts/workspaces/) を、タスク自動化に [mise](https://mise.jdx.dev/) を使用したモダンなPython開発スタックを使用しています。

### 前提条件 (Prerequisites)

- **Python 3.12+**
- **[uv](https://github.com/astral-sh/uv)** - 高速なPythonパッケージマネージャー
- **[mise](https://mise.jdx.dev/)** - 開発環境マネージャー
- **Docker & Docker Compose** - データベースのテスト用（FalkorDB, Redis）

### 開発環境のセットアップ (Setup Development Environment)

```bash
# リポジトリのクローン
git clone https://github.com/kiarina/kiarina-python.git
cd kiarina-python

# 開発環境のセットアップ（ツールのインストール、依存関係の同期、テストデータのダウンロード）
mise run setup

# すべてが動作するか確認
mise run ci
```

### 開発ワークフロー (Development Workflow)

このプロジェクトでは、すべての開発操作に [mise File Tasks](https://mise.jdx.dev/tasks/file-tasks.html) を使用しています：

#### すべてのパッケージ (All Packages)

```bash
# すべてのパッケージのフォーマット
mise run format

# すべてのパッケージのLint実行
mise run lint
mise run lint-fix  # 問題の自動修正

# すべてのパッケージの型チェック
mise run typecheck

# すべてのパッケージのテスト（Dockerサービスが自動的に起動します）
mise run test

# すべてのパッケージのビルド
mise run build

# CIパイプライン全体の実行
mise run ci

# すべてのビルドアーティファクトのクリーンアップ
mise run clean
```

#### 個別のパッケージ (Individual Packages)

```bash
# 特定のパッケージでの作業
mise run package:format kiarina-utils-file
mise run package:lint kiarina-utils-common
mise run package:build kiarina-lib-redis

# カバレッジ付きのテスト
mise run package:test kiarina-utils-file --coverage

# PyPIへの公開
mise run package:publish kiarina-utils-common
mise run package:publish kiarina-lib-redis --test  # Test PyPIへの公開
```

#### ユーティリティタスク (Utility Tasks)

```bash
# 大容量ファイルテスト用のデータダウンロード
mise run download-test-data

# 開発環境をゼロからセットアップ
mise run setup

# 依存関係のアップグレード
mise run upgrade          # uv.lock のみ更新
mise run upgrade --sync   # 更新と環境の同期
```

### プロジェクト構造 (Project Structure)

```
kiarina-python/
├── .github/                    # GitHub Actions ワークフロー
├── .mise/tasks/                # 開発タスクの定義
├── docs/                       # ドキュメント (ナレッジ、プレイブック、ランブック)
├── packages/                   # 個別のパッケージ
│   ├── kiarina/                      # メタパッケージ
│   ├── kiarina-utils-common/         # 共通ユーティリティ
│   ├── kiarina-utils-file/           # ファイル操作
│   ├── kiarina-lib-falkordb/         # FalkorDB 連携
│   ├── kiarina-lib-redis/            # Redis 連携
│   ├── kiarina-lib-redisearch/       # RediSearch 連携
│   ├── kiarina-lib-anthropic/        # Anthropic API 連携
│   ├── kiarina-lib-cloudflare/       # Cloudflare 認証
│   ├── kiarina-lib-cloudflare-d1/    # Cloudflare D1 データベース
│   ├── kiarina-lib-firebase/         # Firebase 認証
│   ├── kiarina-lib-firebase-rtdb/    # Firebase Realtime Database
│   ├── kiarina-lib-google/           # Google Cloud 認証
│   ├── kiarina-lib-openai/           # OpenAI API 連携
│   ├── kiarina-lib-slack/            # Slack API クライアント
├── pyproject.toml             # ワークスペースの設定
├── uv.lock                    # 依存関係のロックファイル
├── docker-compose.yml         # テスト用サービス (Redis, FalkorDB)
└── README.md                  # このファイル
```

### 技術スタック (Technology Stack)

- **言語**: Python 3.12+
- **パッケージ管理**: [uv](https://github.com/astral-sh/uv) (ワークスペース対応)
- **タスクランナー**: [mise](https://mise.jdx.dev/) File Tasks
- **コードフォーマット**: [ruff](https://github.com/astral-sh/ruff)
- **Lint**: [ruff](https://github.com/astral-sh/ruff)
- **型チェック**: [mypy](https://mypy.readthedocs.io/)
- **テスト**: [pytest](https://pytest.org/) (asyncio対応)
- **CI/CD**: GitHub Actions
- **リポジトリスタイル**: uv workspace を使用したモノレポ

### uv ワークスペース構成 (uv Workspace Configuration)

このプロジェクトは効率的なモノレポ管理のために [uv workspace](https://docs.astral.sh/uv/concepts/workspaces/) を活用しています：

- **共有依存関係**: 開発/テストの共通依存関係はルートレベルで管理
- **Editableインストール**: すべてのパッケージは自動的に編集可能(editable)モードでインストール
- **統一されたロックファイル**: 一貫した依存関係解決のための単一の `uv.lock`
- **パッケージ間の依存関係**: パッケージはシームレスに相互依存可能

主要なワークスペース機能:
- `uv sync --all-packages` - すべてのワークスペースパッケージを同期
- `uv build --all` - すべてのパッケージをビルド
- ワークスペースパッケージの自動編集可能インストール
- パッケージソースが分離された共有仮想環境

### テスト (Testing)

このプロジェクトには、特別な考慮事項を含む包括的なテストが含まれています：

- **Dockerサービス**: Redis/FalkorDBを必要とするテストはサービスを自動起動
- **大容量テストデータ**: [kiarina/test-data](https://github.com/kiarina/test-data) のリリースからダウンロード
- **非同期テスト**: async/await パターンの完全サポート
- **カバレッジレポート**: パッケージごと、またはワークスペース全体で利用可能

テストデータの構成:
- `tests/fixtures/` - フィクスチャ用の小さな JSON/YAML ファイル
- `tests/data/small/` - 小さなテストファイル (< 1MB)
- `tests/data/large/` - 大きなテストファイル (別途ダウンロード)

### CI/CD パイプライン (CI/CD Pipeline)

GitHub Actions を使用した自動化されたワークフロー：

- **CI**: すべてのPR/pushでのフォーマット、Lint、型チェック、テスト、ビルド
- **Release**: バージョンタグでの自動リリース
- **Dependency Updates**: 毎週の自動依存関係アップデート
- **Security Audit**: 毎日のセキュリティ脆弱性スキャン

## 🤝 コントリビューション (Contributing)

これは主に個人的なプロジェクトですが、コントリビューションは歓迎します！ 🙂

### 貢献する方法 (How to Contribute)

- **Issues**: バグや機能リクエストについてお気軽にIssueを開いてください
- **Pull Requests**: PRは歓迎しますが、サイドプロジェクトのため対応に時間がかかる場合があります
- **Discussions**: 質問や一般的な議論には GitHub Discussions を使用してください

### 開発ガイドライン (Development Guidelines)

- 既存のコードスタイルに従うこと (ruffで強制)
- 新機能にはテストを追加すること
- 必要に応じてドキュメントを更新すること
- PRを提出する前に `mise run ci` を実行すること

厳格な貢献ガイドラインはありません - テストに合格し、コードが適切にフォーマットされていることを確認してください。

## 📄 ライセンス (License)

このプロジェクトは MIT License の下でライセンスされています。詳細については [LICENSE](LICENSE) ファイルを参照してください。

## 🙏 謝辞 (Acknowledgments)

- **[uv](https://github.com/astral-sh/uv)**: モダンなPythonパッケージ管理とワークスペースサポート
- **[mise](https://mise.jdx.dev/)**: 開発環境とタスク管理
- **[ruff](https://github.com/astral-sh/ruff)**: 高速なPythonリンターおよびフォーマッター
- **[Pydantic](https://pydantic.dev/)**: データ検証と設定管理

---

<div align="center">

**No Programming, No Life.**

*Programming is elegant.*

</div>
