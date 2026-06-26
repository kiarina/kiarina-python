# AGENTS.md

このリポジトリで作業するエージェント向けのガイドラインです。

## 作業前に読むもの

あらゆるタスクを開始する前に、下記を必ず把握してください。
- `pyproject.toml`
- `README.md`
- `.mise/tasks/`
- `Makefile`

また、`docs/` 以下のファイルも、最低限ファイルパスのリストを把握しておいてください。
そして、タスクに関連しそうなファイルの内容は、適宜把握してください。

コードの設計・追加・編集を行う場合、先に下記を把握してください。
- https://github.com/kiarina/crystal-architecture

pydantic-settings に関連したタスクを行う場合は、先に下記を把握してください。
- https://github.com/kiarina/pydantic-settings-manager

リリースする際は、作業前に下記を把握してください。
- docs/runbooks/release/README.md

## README の運用

- 常に `README.md` と `README.ja.md` の両方を作成します。
- `README.md` と `README.ja.md` は、言語違いの完全なミラーとして維持してください。
- README の各ファイルには、言語切り替えのためのリンクを必ず設置してください。
- 対応箇所を見出しで追いやすくするため、`README.ja.md` の `#`, `##`, `###`, `####` などの見出しは `README.md` と同じ英語に必ず一致させてください。
- README の内容の精査段階では、先行して `README.ja.md` を作成して、内容が確定したら `README.md` を作成するのが望ましいです。

## 変更後の確認

コードを変更した場合は、`make` を実行して、build が通るか確認してください。

```bash
make
```

また、修正したパッケージのテストが通るか確認してください。

```bash
mise run test <package_name>
```

全体のテストは下記で実行できます。

```bash
make test
```

## commit message と Pull Request タイトルの書き方

- commit message も、英語で `type(scope): subject` の Conventional Commits 形式で記述してください。
- Pull Request タイトルは、英語で `type(scope): subject` の Conventional Commits 形式で記述してください。
- 変更が特定のパッケージに限定される場合は、scope にそのパッケージ名を含めてください。
- 変更が複数のパッケージにまたがる場合は、scope に複数のパッケージ名をカンマ区切りで含めてください。
- 変更内容がプロジェクト全体に影響する場合は、scope は省略可能です。

## CHANGELOG の運用

コードの変更を commit する場合は、commit 直前に `CHANGELOG.md` の `Unreleased` セクションへ変更内容を追記し、コードの変更と同じ commit に含めてください。commit するまでは `CHANGELOG.md` を更新しないでください。

## テスト用のアセットの管理

テスト用のアセット（テキストファイルやバイナリファイルなど）は、下記で管理します。
- https://github.com/kiarina/test-assets

下記のコマンドを実行すると、`./tests/assets/` にダウンロードされます。
```sh
mise run test-assets:download
```

`./tests/assets/` は、各パッケージのテストで共有します。
