# uv Workspace Operations

[English](README.md) | [日本語](README.ja.md)

uv workspace を使用するプロジェクトの運用ルールです。

- 全パッケージ共通の dev / test パッケージはルートで管理します
- LICENSE ファイルはルートに配置します
- CHANGELOG は各パッケージとルートに配置します。ルートには全体の変更履歴の概要を記載します
- uv 関連コマンドは mise File Tasks に定義し、mise run 経由で実行します
