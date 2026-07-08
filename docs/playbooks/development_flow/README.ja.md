# Development Flow

[English](README.md) | 日本語

開発依頼または修正依頼を受けてから、開発、テスト、Pull Request 作成までを行うプロセスです。

### Receiving Tasks

新機能開発の依頼かどうかを判断します。

- 例: 「〜を追加してください」「〜を改善してください」「〜を修正してください」など

依頼内容を正確に理解します。

- 依頼内容が不明確な場合は、詳細を確認します。

---

### Design, Implementation, and Testing

依頼内容に基づいて、新機能の設計を検討します。

- 既存機能との一貫性を考慮します。
- 認知負荷の低い設計を目指します。

main branch から development branch を作成します。

development branch に実装を commit します。

テストを実装します。

次を実行して Lint（auto fix）、Format、Type Check、Test を行い、問題がないことを確認します。

`cd packages/$package_name && make check`

すべてのパッケージのテストを実行し、問題がないことを確認します。

`mise run ci`

---

### Makefile Style

`.PHONY` は、基本的に 1 行にまとめます。

改行が必要になる場合は、まとめて書かず、各タスクの直前にそれぞれ書きます。

pytest marker の使い方は [Pytest Markers](../pytest_markers/README.ja.md) を参照します。

```make
.PHONY: image_generation_provider_openai_test
image_generation_provider_openai_test:
	mise run test --costly --path tests/image_generation_provider_impl/openai

.PHONY: image_generation_model_test
image_generation_model_test:
	mise run test --costly --path tests/image_generation_model
```

---

### Updating CHANGELOG.md

PyPI に公開される機能の変更については、対象 sub project、meta project、root project の CHANGELOG.md に記録します。

- sub project の CHANGELOG.md を更新します: `packages/{package_name}/CHANGELOG.md`
  - 詳細な更新内容を記録します
- meta package project の CHANGELOG.md を更新します: `packages/kiarina/CHANGELOG.md`
  - 各項目を 1 行で簡潔に記録します
- root project の CHANGELOG.md を更新します: `CHANGELOG.md`
  - 各項目を 1 行で簡潔に記録します

CHANGELOG.md の更新を commit して push します。

---

### Creating a Pull Request

gh command を使用して main branch に対する Pull Request を作成します。

- tmp file に書いた body を reference として使用します

Pull Request に review が付いたら、feedback に対応します。
discussion の一覧は `gh discussion list` で確認できます。
discussion は `gh discussion view <number> --comments` で確認できます。
