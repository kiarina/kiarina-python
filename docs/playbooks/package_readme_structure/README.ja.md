# Package README Structure

[English](README.md) | 日本語

各パッケージの `README.md` と `README.ja.md` で使用する標準的な見出し構成です。

## Principles

- `README.md` と `README.ja.md` は、言語違いの完全なミラーとして維持します。
- 両ファイルの見出しは、同じ英語、同じ階層、同じ順序にします。
- 見出しだけで、パッケージの依存関係、導入方法、主な用途、公開 API を順に把握できる構成にします。
- 公開 API は、内部のファイル構成ではなく、利用者が import する公開パスを基準に記載します。
- パッケージ固有の情報がない見出しは、空のまま残さず省略します。

## Standard Structure

通常のライブラリパッケージでは、次の順序を標準とします。

```markdown
# <package-name>

[English](README.md) | 日本語

<badges>

> [!NOTE] これは何？
> <パッケージの役割を一文で説明>

## Dependencies

## Installation

## Features

### <Use Case or Feature>

## API Reference

### `<Public API>`
```

英語版の言語切り替えは次のようにします。

```markdown
English | [日本語](README.ja.md)
```

## Required Sections

### Package Title

H1 には PyPI のパッケージ名を記載します。

```markdown
# kiarina-utils-common
```

タイトル直後には言語切り替えリンク、PyPI・Python・License などの badge、パッケージの役割を説明する NOTE を配置します。

NOTE は詳細な機能一覧ではなく、「何を提供するパッケージか」を一文で説明します。

### Dependencies

利用者が導入する runtime dependency を表で記載します。

```markdown
## Dependencies

| Package | Version | License |
| --- | --- | --- |
| [Pydantic](https://github.com/pydantic/pydantic) | `>=2.0.0` | [MIT](https://github.com/pydantic/pydantic/blob/main/LICENSE) |
```

Python 標準ライブラリだけを使用する場合は、その旨を簡潔に記載します。
development dependency や test dependency は含めません。

### Installation

PyPI からパッケージ単体を導入する最小のコマンドを記載します。

````markdown
## Installation

```bash
pip install <package-name>
```
````

optional dependency がある場合は、`### Optional Dependencies` を追加できます。

### Features

利用者が実現できることを、ユースケース単位で説明します。
最初に機能の一覧を示し、詳しい説明が必要な項目は同名の H3 を追加します。

```markdown
## Features

- **<Use Case>**
  <利用者が実現できること>

### <Use Case>

<説明と実行可能な例>
```

見出しには、内部の class 名や module 名だけでなく、利用者の目的が伝わる名前を優先します。
コード例は公開 API から import し、最小限の前提で実行できる内容にします。

### API Reference

パッケージが公開する API を、function、class、instance などの公開要素ごとに記載します。

````markdown
## API Reference

### `<Public API>`

```python
<signature or minimal usage>
```

<概要>

**Parameters**

- `<name>` (`<type>`): <説明>

**Returns**

- `<type>`: <説明>

**Raises**

- `<Exception>`: <発生条件>

**Examples**

```python
<example>
```
````

該当しない項目は省略できます。
公開 API の並びは、基本的な function、主要な class、補助的な型・instance の順を目安にします。
