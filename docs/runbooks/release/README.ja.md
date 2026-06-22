# Release

[English](README.md) | [日本語](README.ja.md)

kiarina-python を PyPI にリリースするための手順です。

このガイドでは、バージョン 1.0.0 を例にリリース手順を説明します。

## v1.0.0 Release Procedure

### 1. Update Version

```sh
# Update all packages to version 1.0.0
mise run version:update 1.0.0
```

### 2. Update CHANGELOG

ルートと各パッケージの `CHANGELOG.md` ファイルを確認し、更新します。

まず、次の `CHANGELOG.md` ファイルの `Unreleased` セクションに更新内容を追加します。

- ルート `CHANGELOG.md`: 全パッケージの変更概要（変更ごとに 1 行）
- `packages/kiarina/CHANGELOG.md`: kiarina メタパッケージ用に、ルートと同じ内容
- `packages/<package-name>/CHANGELOG.md`: 各パッケージの詳細な変更内容

次に、以下の mise task を実行し、CHANGELOG の `Unreleased` セクションを `v1.0.0` セクションに置き換えます。

```sh
mise run changelog:update 1.0.0
```

この task は、更新がないパッケージに対して自動的に `No changes` エントリを追加します。

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
git commit -m "chore: bump version to 1.0.0"

# Create annotated tag
git tag -s v1.0.0 -m "Release v1.0.0"

# Push with tags
git push --tags
```

## Automated Processes

タグを push すると、GitHub Actions の `.github/workflows/release.yml` workflow が次のプロセスを自動実行します。

1. **CI Checks**: lint、test、build を実行します
2. **GitHub Release**: release notes 付きの GitHub Release を自動作成します
3. **PyPI Publication**: すべてのパッケージを PyPI に公開します（`PYPI_API_TOKEN` が設定されている場合）
