# kiarina

[English](README.md) | [日本語](README.ja.md)

[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/kiarina.svg)](https://badge.fury.io/py/kiarina)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/kiarina/kiarina-python/blob/main/LICENSE)

> **kiarina's Python utility collection** - 現代的な Python 開発に必要なユーティリティをまとめて導入できる namespace package collection です。

## 🚀 Quick Install

すべての kiarina パッケージを 1 つのコマンドでインストールできます。

```bash
pip install kiarina
```

このメタパッケージは、主要なユーティリティ、クラウド連携、データベース連携パッケージをまとめてインストールします。

- **kiarina-i18n** - シンプルな国際化 (i18n) ユーティリティ
- **kiarina-currency** - 通貨と為替レートのユーティリティ
- **kiarina-utils-common** - 共通ユーティリティとヘルパー関数
- **kiarina-utils-file** - エンコーディング検出つきの高度なファイル I/O
- **kiarina-lib-anthropic** - Anthropic API 連携ユーティリティ
- **kiarina-lib-cloudflare** - Cloudflare 認証ユーティリティ
- **kiarina-lib-cloudflare-d1** - Cloudflare D1 database 連携
- **kiarina-lib-falkordb** - FalkorDB 連携ユーティリティ
- **kiarina-lib-firebase** - Firebase 認証ユーティリティ
- **kiarina-lib-firebase-rtdb** - Firebase Realtime Database 連携
- **kiarina-lib-google** - Google Cloud 認証ユーティリティ
- **kiarina-lib-openai** - OpenAI API 連携ユーティリティ
- **kiarina-lib-redis** - 設定管理つき Redis 連携
- **kiarina-lib-redisearch** - RediSearch 連携とクエリビルダー
- **kiarina-lib-slack** - Slack API クライアント設定

## 📖 Usage

インストール後は、必要な kiarina パッケージを個別に import して利用できます。

```python
from kiarina.utils.common import parse_config_string

config = parse_config_string("app.debug=true&db.port=5432")
```

```python
import kiarina.utils.file as kf

blob = kf.read_file("document.txt")
data = kf.read_json_dict("config.json", default={})
```

```python
import kiarina.utils.file.asyncio as kfa

blob = await kfa.read_file("large_file.dat")
```

```python
from kiarina.lib.redis import get_redis

redis = get_redis()
```

## 🎯 Individual Package Installation

必要な機能だけを使う場合は、個別パッケージをインストールできます。

```bash
pip install kiarina-utils-common kiarina-utils-file
pip install kiarina-lib-redis kiarina-lib-falkordb kiarina-lib-redisearch
```

## 📚 Documentation

詳細なドキュメント、例、API リファレンスはメインリポジトリを参照してください。

**[Full Documentation](https://github.com/kiarina/kiarina-python#readme)**

## 🤝 Contributing

主に個人用途で開発しているプロジェクトですが、issue や pull request は歓迎します。詳細は [main repository](https://github.com/kiarina/kiarina-python) を参照してください。

## 📄 License

このプロジェクトは MIT License のもとで公開されています。詳細は [LICENSE](https://github.com/kiarina/kiarina-python/blob/main/LICENSE) を参照してください。

