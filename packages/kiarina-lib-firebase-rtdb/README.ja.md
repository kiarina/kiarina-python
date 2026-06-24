# kiarina-lib-firebase-rtdb

[English](README.md) | 日本語

kiarina namespace 向けの Firebase Realtime Database library です。

## Purpose

Firebase Realtime Database の REST API を使って、agent 向けの real-time state synchronization と data persistence を扱います。

## Installation

```bash
pip install kiarina-lib-firebase-rtdb
```

```bash
uv add kiarina-lib-firebase-rtdb
```

## Quick Start

### Basic Data Retrieval

```python
from kiarina.lib.firebase import TokenManager
from kiarina.lib.firebase_rtdb import get_data

token_manager = TokenManager(api_key="api-key", refresh_token="refresh-token")
data = await get_data("/agents/state", token_manager=token_manager)
```

### Real-time Data Watching

```python
from kiarina.lib.firebase_rtdb import watch_data

async for event in watch_data("/agents/state", token_manager=token_manager):
    print(event.event_type, event.path, event.data)
```

## API Reference

### get_data()

指定 path の data を Firebase RTDB REST API から取得します。

### watch_data()

Server-Sent Events を使って指定 path の変更を監視します。

### DataChangeEvent

RTDB の data change event を表す schema です。

### RTDBStreamCancelledError

stream cancellation を表す exception です。

## Configuration

### Using pydantic-settings-manager

pydantic-settings-manager を使って database URL、retry 設定などを管理できます。

### YAML Configuration Example

```yaml
kiarina.lib.firebase_rtdb:
  database_url: "https://your-project-default-rtdb.firebaseio.com"
  retry_initial_delay: 1.0
  retry_max_delay: 30.0
```

### Environment Variables

```bash
export KIARINA_LIB_FIREBASE_RTDB_DATABASE_URL="https://your-project-default-rtdb.firebaseio.com"
```

### RTDBSettings

database URL、retry delay、timeout などを保持する settings model です。

## Advanced Usage

### Custom Stop Logic

`watch_data()` の async iterator を application 側の条件で break することで、監視を停止できます。

### Error Handling

network error には retry が適用されます。stream を明示的に停止する場合は cancellation を扱います。

## Testing

### Setup Test Environment

Firebase test project と `.env` を用意して統合テストを実行します。

### Run Tests

```bash
mise run package:test kiarina-lib-firebase-rtdb
mise run package:test kiarina-lib-firebase-rtdb --coverage
```

## Dependencies

- `httpx`
- `kiarina-lib-firebase`
- `pydantic`
- `pydantic-settings`
- `pydantic-settings-manager`

## License

MIT License です。詳細は [LICENSE](../../LICENSE) を参照してください。

## Related Projects

- [kiarina-python](https://github.com/kiarina/kiarina-python)
- [Firebase Realtime Database](https://firebase.google.com/docs/database)

## Resources

- [Firebase REST API](https://firebase.google.com/docs/database/rest/start)

