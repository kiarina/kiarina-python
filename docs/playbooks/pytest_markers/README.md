# Pytest Markers

English | [日本語](README.ja.md)

This guide explains how to use `pytest.mark.costly` and `pytest.mark.downloads_model`.

### costly

Use this marker for pytest tests that are costly and should not run every time.

Authentication is not part of the condition.

These tests are skipped by the default `mise run test`. To run them, use one of the following.

```bash
mise run test <package> --costly
KIARINA_TEST_COSTLY=1 mise run test <package>
```

### downloads_model

Use this marker for pytest tests that download heavy files such as models.

These tests run normally on local machines. They are skipped on GitHub Actions because `GITHUB_ACTIONS=true`.

### How to Mark Tests

To mark one test function:

```python
@pytest.mark.costly
def test_example() -> None:
    ...
```

To mark a whole file:

```python
pytestmark = [pytest.mark.downloads_model]
```

If a test is costly and also downloads heavy files, use both markers.

```python
pytestmark = [pytest.mark.costly, pytest.mark.downloads_model]
```
