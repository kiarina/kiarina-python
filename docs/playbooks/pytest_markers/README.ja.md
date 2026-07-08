# Pytest Markers

[English](README.md) | 日本語

`pytest.mark.costly` と `pytest.mark.downloads_model` の使い方です。

### costly

コストが高く、毎回実行したくない pytest に付けます。

認証の有無は条件にしません。

通常の `mise run test` では skip されます。実行する場合は、次のどちらかを使います。

```bash
mise run test <package> --costly
KIARINA_TEST_COSTLY=1 mise run test <package>
```

### downloads_model

モデルなどの重いファイルの download を伴う pytest に付けます。

ローカルでは通常どおり実行されます。GitHub Actions では `GITHUB_ACTIONS=true` のため skip されます。

### How to Mark Tests

関数単位で付ける場合:

```python
@pytest.mark.costly
def test_example() -> None:
    ...
```

ファイル全体に付ける場合:

```python
pytestmark = [pytest.mark.downloads_model]
```

コストが高く、かつ重いファイルも download する場合は、両方付けます。

```python
pytestmark = [pytest.mark.costly, pytest.mark.downloads_model]
```
