# External Service Tests

English | [日本語](README.ja.md)

This guide explains how to write tests that depend on external services (local servers or external APIs).

Tests must be skipped, not errored, when the external service is unavailable.

## Settings Loading and Skip

Place a git-ignored `test_settings.yaml` in the test directory and load it with an autouse fixture.
Skip when the file is missing or empty.

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

`test_settings.yaml` is excluded by `.gitignore`, so it does not exist on GitHub Actions.
With this fixture, tests that depend on external services are automatically skipped in CI.

## Health Check and Skip

Run a health check in an autouse fixture before accessing the external service.

Always wrap the health check in `try-except`.
Skip on connection failures, timeouts, and non-200 responses alike.

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

Without the exception handling, an unreachable server produces a fixture error (`ERROR at setup`) instead of a skip.

Reference implementations:
- `packages/kiarina-agi-image/tests/image_generation_provider_impl/kiapi/conftest.py`
- `packages/kiarina-agi-video/tests/video_generation_provider_impl/kiapi/conftest.py`

## Costly Calls

Mark costly tests that perform actual generation with `pytest.mark.costly`.

See [Pytest Markers](../pytest_markers/README.md) for details.

## Sharing Settings

See [kiarina/test-settings](https://github.com/kiarina/test-settings) for how to share `test_settings.yaml`.
