# Implementation Optional Dependencies

English | [日本語](README.ja.md)

Dependencies used only under `{mod}_impl.{name}` must be optional dependencies.

Name the extra `{mod}-{name}` and replace `_` with `-`.

For example, define dependencies for `asset_repository_impl.gcs` as follows:

```toml
[project.optional-dependencies]
asset-repository-gcs = [
    "google-cloud-storage>=3.4.0",
]
```

Wrap dependency imports in `try-except`. On `ImportError`, identify the class or feature that requires the dependency and suggest the extra installation command.

```python
try:
    import google.cloud.exceptions
    from google.cloud.storage import Blob, Client
except ImportError as exc:
    raise ImportError(
        "google-cloud-storage is required to use GCSAssetRepository. "
        "Install it with: "
        "pip install 'kiarina-agi-file[asset-repository-gcs]'"
    ) from exc
```
