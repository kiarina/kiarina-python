# Implementation Optional Dependencies

[English](README.md) | 日本語

`{mod}_impl.{name}` 以下でのみ使用する依存パッケージは、optional dependency にします。

extra 名は `{mod}-{name}` とし、`_` は `-` に置き換えます。

例えば、`asset_repository_impl.gcs` の依存は次のように定義します。

```toml
[project.optional-dependencies]
asset-repository-gcs = [
    "google-cloud-storage>=3.4.0",
]
```

依存パッケージの import は `try-except` で囲みます。`ImportError` では、利用するクラスまたは機能と extra のインストールコマンドを案内します。

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
