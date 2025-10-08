---
title: Security Policy for Sensitive Data
description: >-
  Guidelines for handling sensitive data (credentials, API keys, passwords) in kiarina-python packages.
  Use Pydantic's SecretStr to prevent accidental exposure in logs and debug output.
---

## Overview

All kiarina-python packages must protect sensitive data from accidental exposure in logs, debug output, and string representations. This is achieved using Pydantic's `SecretStr` type.

## What is Sensitive Data?

Sensitive data includes any information that could compromise security if exposed:

- **Authentication credentials**: Service account keys, OAuth tokens, refresh tokens
- **API keys and secrets**: Cloud provider API keys, client secrets
- **Passwords and tokens**: Database passwords, connection strings with embedded credentials
- **Private keys**: Cryptographic keys, signing keys

## Policy: Use SecretStr for Sensitive Data

### Rule

All configuration fields containing sensitive data **MUST** use `SecretStr` instead of `str`.

### Rationale

1. **Defense in Depth**: Prevents accidental exposure even if developers use `print()` or log settings objects
2. **Explicit Access**: Forces developers to consciously access sensitive data via `.get_secret_value()`
3. **Low Implementation Cost**: Minimal code changes required
4. **Standard Practice**: Follows Pydantic's recommended security practices

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

Use `SecretStr` for sensitive fields:

```python
from pydantic import SecretStr
from pydantic_settings import BaseSettings

class GoogleAuthSettings(BaseSettings):
    service_account_data: SecretStr | None = None
    client_secret_data: SecretStr | None = None
    authorized_user_data: SecretStr | None = None
```

### 2. Accessing Secret Values

Provide helper methods to access parsed secret values:

```python
import json
from typing import Any

class GoogleAuthSettings(BaseSettings):
    service_account_data: SecretStr | None = None

    def get_service_account_data(self) -> dict[str, Any] | None:
        if not self.service_account_data:
            return None
        return json.loads(self.service_account_data.get_secret_value())
```

### 3. Direct Access (When Necessary)

If direct access is needed, use `.get_secret_value()`:

```python
settings = GoogleAuthSettings(service_account_data='{"key": "value"}')

# Access the secret value
secret_value = settings.service_account_data.get_secret_value()
```
