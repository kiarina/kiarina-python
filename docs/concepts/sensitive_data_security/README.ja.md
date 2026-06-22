# Sensitive Data Security

[English](README.md) | [日本語](README.ja.md)

kiarina-python パッケージで機密データを扱うためのガイドラインです。

## Overview

すべての kiarina-python パッケージは、ログ、デバッグ出力、文字列表現で機密データが誤って露出しないように保護する必要があります。これは Pydantic の `SecretStr` 型を使用して実現します。

## What is Sensitive Data?

機密データには、露出するとセキュリティを損なう可能性があるあらゆる情報が含まれます。

- **認証情報**: サービスアカウントキー、OAuth トークン、リフレッシュトークン
- **API キーとシークレット**: クラウドプロバイダーの API キー、クライアントシークレット
- **パスワードとトークン**: データベースパスワード、認証情報を含む接続文字列
- **秘密鍵**: 暗号鍵、署名鍵

## Policy: Use SecretStr for Sensitive Data

### Rule

機密データを含むすべての設定フィールドは、`str` ではなく **必ず** `SecretStr` を使用してください。

### Rationale

1. **多層防御**: 開発者が設定オブジェクトを `print()` したりログ出力したりしても、偶発的な露出を防ぎます
2. **明示的なアクセス**: `.get_secret_value()` を通じて、開発者が機密データへ意識的にアクセスすることを強制します
3. **低い実装コスト**: 必要なコード変更は最小限です
4. **標準的な慣行**: Pydantic が推奨するセキュリティプラクティスに従います

### Example

```python
from pydantic import SecretStr
from pydantic_settings import BaseSettings

class MySettings(BaseSettings):
    # ❌ Bad: Plain string
    api_key: str

    # ✅ Good: SecretStr
    api_key: SecretStr

    # ❌ Bad: Plain string with password
    database_url: str = "postgresql://user:password@localhost/db"

    # ✅ Good: SecretStr for URLs with credentials
    database_url: SecretStr = SecretStr("postgresql://user:password@localhost/db")
```

## Implementation Guidelines

### 1. Field Declaration

機密フィールドには `SecretStr` を使用します。

```python
from pydantic import SecretStr
from pydantic_settings import BaseSettings

class GoogleSettings(BaseSettings):
    service_account_data: SecretStr | None = None
    client_secret_data: SecretStr | None = None
    authorized_user_data: SecretStr | None = None
```

### 2. Accessing Secret Values

パース済みのシークレット値へアクセスするためのヘルパーメソッドを提供します。

```python
import json
from typing import Any

class GoogleSettings(BaseSettings):
    service_account_data: SecretStr | None = None

    def get_service_account_data(self) -> dict[str, Any] | None:
        if not self.service_account_data:
            return None
        return json.loads(self.service_account_data.get_secret_value())
```

### 3. Direct Access (When Necessary)

直接アクセスが必要な場合は、`.get_secret_value()` を使用します。

```python
settings = GoogleSettings(service_account_data='{"key": "value"}')

# Access the secret value
secret_value = settings.service_account_data.get_secret_value()
```
