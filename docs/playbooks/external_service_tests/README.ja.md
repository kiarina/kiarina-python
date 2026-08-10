# External Service Tests

[English](README.md) | 日本語

外部サービス（ローカルサーバーや外部 API）に依存するテストの書き方です。

外部サービスが利用できない環境でも、テストは error にならず skip になる必要があります。

## Settings Loading and Skip

テストディレクトリに git-ignored な `test_settings.yaml` を置き、autouse fixture で読み込みます。
ファイルがない、または空の場合は skip します。

```python
@pytest.fixture(autouse=True)
def setup_settings() -> Iterator[None]:
    settings_path = Path(__file__).resolve().parent / "test_settings.yaml"

    if not settings_path.is_file():
        pytest.skip(f"test_settings.yaml does not exist: {settings_path}")

    user_configs = read_yaml_dict(settings_path)

    if not user_configs:
        pytest.skip(f"test_settings.yaml is empty: {settings_path}")

    load_user_configs(user_configs)
    yield
    clear_user_configs(user_configs)
```

`test_settings.yaml` は `.gitignore` で除外されているため、GitHub Actions には存在しません。
この fixture により、CI では外部サービス依存のテストが自動的に skip されます。

## Health Check and Skip

外部サービスへのアクセスは、autouse fixture で health check してから行います。

health check は必ず `try-except` で囲みます。
接続不可、タイムアウト、非 200 のいずれも skip にします。

```python
@pytest.fixture(autouse=True)
def check_health(setup_settings: None) -> None:
    import httpx

    from kiarina.agi.image_generation_provider_impl.kiapi import settings_manager

    url = f"{settings_manager.settings.kiapi_base_url}/health"

    try:
        response = httpx.get(url, timeout=2.0)
        response.raise_for_status()
    except Exception as exc:
        pytest.skip(f"kiapi is not healthy: {url} ({exc})")
```

例外を捕捉しない場合、サーバーに接続できないと skip ではなく fixture の error（`ERROR at setup`）になります。

参考実装:
- `packages/kiarina-agi-image/tests/image_generation_provider_impl/kiapi/conftest.py`
- `packages/kiarina-agi-video/tests/video_generation_provider_impl/kiapi/conftest.py`

## Costly Calls

実際に生成などを行うコストの高いテストには `pytest.mark.costly` を付けます。

詳細は [Pytest Markers](../pytest_markers/README.ja.md) を参照してください。

## Sharing Settings

`test_settings.yaml` の共有方法は [kiarina/test-settings](https://github.com/kiarina/test-settings) を参照してください。
