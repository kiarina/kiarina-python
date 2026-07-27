# Release

[English](README.md) | 日本語

kiarina-python を PyPI にリリースするための手順です。

このガイドでは、バージョン 2.2.0 を例にリリース手順を説明します。

## v2.2.0 Release Procedure

### 1. Update Version

version を更新する前に、次の `Unreleased` セクションへリリース内容を追加します。

- ルート `CHANGELOG.md`: 全パッケージの変更概要
- `packages/kiarina/CHANGELOG.md`: `kiarina` メタパッケージ用の同じ概要
- `packages/<package-name>/CHANGELOG.md`: 変更された各パッケージの詳細

```sh
# Update the root, kiarina, and packages with unreleased changes
mise run pyproject:bump-version 2.2.0
```

ルートプロジェクトと `kiarina` メタパッケージは常に更新されます。その他の
パッケージは、`Unreleased` セクションに変更内容がある場合だけ更新されます。
対象パッケージについては、メタパッケージの依存version下限も更新されます。

### 2. Update CHANGELOG

ルートと、version が `2.2.0` に一致するパッケージについて、`Unreleased` を
リリースversionへ置き換えます。

```sh
mise run changelog:bump-version 2.2.0
```

version がリリースversionと一致しないパッケージは変更されません。対象パッケージの
changelog に内容がない場合、task は失敗します。

### 3. Review Changes

```sh
# Review changed files
git diff
```

### 4. Run CI Checks

```sh
# Ensure all CI checks pass
mise run ci
```

### 5. Commit, Tag, and Push

```sh
# Commit changes
git add .
git commit -m "chore: bump version to 2.2.0"

# Create annotated tag
git tag -s v2.2.0 -m "Release v2.2.0"

# Push with tags
git push --tags
```

## First Release of a New Package

PyPI 公開は Trusted Publishing（OIDC）を使用しており、新規の PyPI プロジェクトを作成できません。新しいパッケージを初めてリリースする前に、https://pypi.org/manage/account/publishing/ で **pending publisher** を登録してください。

| Field | Value |
| --- | --- |
| PyPI Project Name | `<new-package-name>` |
| Owner | `kiarina` |
| Repository name | `kiarina-python` |
| Workflow name | `release-pypi.yml` |
| Environment name | `pypi` |

登録を忘れると、release job は新パッケージのアップロード時点で `400 Non-user identities cannot create new projects` で失敗し、一部のパッケージだけがアップロード済みの状態になることがあります。pending publisher を登録してから失敗した job を再実行してください。`skip-existing: true` により再実行は安全です（2026-07-28、v2.20.0 で発生）。

## Automated Processes

タグを push すると、GitHub Actions の `.github/workflows/release-pypi.yml` workflow が次のプロセスを自動実行します。

1. **CI Checks**: lint、test、build を実行します
2. **GitHub Release**: release notes 付きの GitHub Release を自動作成します
3. **Release Build**: tag とversionが一致するパッケージだけをbuildします
4. **PyPI Publication**: すべてのリリース対象パッケージを Trusted Publishing（OIDC）で一度の処理で公開します
