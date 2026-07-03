# kiarina-agi-base

[English](README.md) | 日本語

[![PyPI version](https://badge.fury.io/py/kiarina-agi-base.svg)](https://badge.fury.io/py/kiarina-agi-base)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-agi-base.svg)](https://pypi.org/project/kiarina-agi-base/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> [!NOTE] What is this?
> AI agent の実行 context、cost の記録、request logging、token 見積もりに共通して必要な型と機能を提供します。

## Dependencies

| Package | Version | License |
| --- | --- | --- |
| [jaxtyping](https://github.com/patrick-kidger/jaxtyping) | `>=0.3.3` | [MIT](https://github.com/patrick-kidger/jaxtyping/blob/main/LICENSE) |
| [kiarina-currency](../kiarina-currency/) | `>=2.3.1` | [MIT](../../LICENSE) |
| [kiarina-i18n](../kiarina-i18n/) | `>=2.3.1` | [MIT](../../LICENSE) |
| [kiarina-utils-app](../kiarina-utils-app/) | `>=2.3.0` | [MIT](../../LICENSE) |
| [kiarina-utils-common](../kiarina-utils-common/) | `>=2.3.0` | [MIT](../../LICENSE) |
| [kiarina-utils-file](../kiarina-utils-file/) | `>=2.3.1` | [MIT](../../LICENSE) |
| [NumPy](https://github.com/numpy/numpy) | `>=2.0` | [BSD-3-Clause](https://github.com/numpy/numpy/blob/main/LICENSE.txt) |
| [Pydantic](https://github.com/pydantic/pydantic) | `>=2.11.7` | [MIT](https://github.com/pydantic/pydantic/blob/main/LICENSE) |
| [pydantic-settings](https://github.com/pydantic/pydantic-settings) | `>=2.10.1` | [MIT](https://github.com/pydantic/pydantic-settings/blob/main/LICENSE) |
| [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) | `>=3.2.0` | [MIT](https://github.com/kiarina/pydantic-settings-manager/blob/main/LICENSE) |
| [PyYAML](https://github.com/yaml/pyyaml) | `>=6.0.2` | [MIT](https://github.com/yaml/pyyaml/blob/main/LICENSE) |
| [tiktoken](https://github.com/openai/tiktoken) | `>=0.13.0` | [MIT](https://github.com/openai/tiktoken/blob/main/LICENSE) |

## Installation

```bash
pip install kiarina-agi-base
```

## Features

- **Run context**
  アプリケーション、organization、user、agent、node、locale、metadata を実行単位で保持します。
- **Cost recording**
  Cost をメモリに集約し、console に表示するか、ローカルの JSON Lines ファイルへ保存します。
- **Request logging**
  成功・失敗した request の内容を console またはローカルの Markdown ファイルへ出力します。
- **Token estimation**
  Text、image、audio、video、PDF の token 数を見積もります。
- **Formatting and media types**
  Console、cost、file reference の整形と、型付き image array を提供します。

### Run Context

必要な識別子を環境変数で設定してから `RunContext` を作成します。

```bash
export KIARINA_AGI_RUN_CONTEXT_ORGANIZATION_ID=my-org
export KIARINA_AGI_RUN_CONTEXT_USER_ID=my-user
export KIARINA_AGI_RUN_CONTEXT_AGENT_ID=my-agent
export KIARINA_AGI_RUN_CONTEXT_NODE_ID=my-node
export KIARINA_AGI_RUN_CONTEXT_TIME_ZONE=Asia/Tokyo
export KIARINA_AGI_RUN_CONTEXT_LANGUAGE=ja
export KIARINA_AGI_RUN_CONTEXT_CURRENCY=JPY
```

```python
from kiarina.agi.run_context import RunContext
from kiarina.utils.app import configure

configure("example-app", "example-author")
run_context = RunContext().with_metadata(request_id="req-123")
print(run_context.zone_info)
```

### Cost Recording

Registry は preset 名、または `name?key=value` 形式の specifier から実装を解決します。`local` recorder は user data directory の `costs.jsonl` に保存します。

```python
import asyncio

from kiarina.agi.cost_record import CostRecord
from kiarina.agi.cost_recorder import cost_recorder_registry
from kiarina.agi.run_context import RunContext
from kiarina.utils.app import configure


async def main() -> None:
    configure("example-app", "example-author")
    recorder = cost_recorder_registry.resolve("local")
    recorder.add(
        CostRecord(
            microdollars=125_000,
            kind="chat",
            source="example-model",
        )
    )
    await recorder.flush(RunContext())


asyncio.run(main())
```

利用可能な cost logger preset は `console` と `null`、cost recorder preset は `local` と `null` です。既定値はいずれも `null` です。

### Request Logging

利用可能な preset は `console`、`local`、`null` です。`local` logger は user cache directory 以下へ Markdown を保存します。

```python
import asyncio

from kiarina.agi.request_logger import (
    RequestLogEntry,
    request_logger_registry,
)
from kiarina.agi.run_context import RunContext
from kiarina.utils.app import configure


async def main() -> None:
    configure("example-app", "example-author")
    logger = request_logger_registry.resolve("console")
    await logger.log_request_success(
        RequestLogEntry(
            kind="chat",
            source="example-model",
            content="# Request\n\nHello",
        ),
        run_context=RunContext(),
    )


asyncio.run(main())
```

### Token Estimation

見積もりは model や provider によって異なります。Text では `TokenUtilsSettings.tiktoken_model_name`、image では OpenAI の tile 計算、audio と video では時間ベースの係数を使用します。

```python
from kiarina.agi.token_utils import (
    ImageSize,
    calc_image_token,
    calc_text_token,
)

text_tokens = calc_text_token("Hello, world!")
image_tokens = calc_image_token(ImageSize(width=1024, height=768))
```

## API Reference

### `kiarina.agi.run_context`

```python
from kiarina.agi.run_context import (
    IDStr,
    RunContext,
    RunContextSettings,
    TimeZone,
    get_node_id,
    settings_manager,
)
```

#### `get_node_id`

```python
def get_node_id() -> str: ...
```

現在の設定から node ID を返します。未設定の場合は `ValueError` を送出します。

#### `RunContext`

```python
class RunContext(BaseModel):
    app_author: str = <configured app author>
    app_name: str = <configured app name>
    organization_id: IDStr = <configured organization ID>
    user_id: IDStr = <configured user ID>
    agent_id: IDStr = <configured agent ID>
    node_id: IDStr = <configured node ID>
    time_zone: TimeZone = "UTC"
    language: Language = "en"
    currency: CurrencyCode = "USD"
    metadata: dict[str, Any] = {}

    @property
    def zone_info(self) -> ZoneInfo: ...

    def with_metadata(self, **kwargs: Any) -> Self: ...
```

`with_metadata` は既存の metadata を更新した copy を返します。

#### `RunContextSettings`

```python
class RunContextSettings(BaseSettings):
    organization_id: IDStr | None = None
    user_id: IDStr | None = None
    agent_id: IDStr | None = None
    node_id: IDStr | None = None
    time_zone: TimeZone = "UTC"
    language: Language = "en"
    currency: CurrencyCode = "USD"

    def get_organization_id(self) -> IDStr: ...
    def get_user_id(self) -> IDStr: ...
    def get_agent_id(self) -> IDStr: ...
    def get_node_id(self) -> IDStr: ...
```

環境変数 prefix は `KIARINA_AGI_RUN_CONTEXT_` です。各 `get_*_id` は値が未設定の場合に `ValueError` を送出します。

#### `IDStr`

```python
IDStr = Annotated[
    str,
    StringConstraints(min_length=1, pattern=r"^[a-zA-Z0-9._-]+$"),
]
```

#### `TimeZone`

```python
TimeZone: TypeAlias = str
```

IANA time zone 名です。

#### `settings_manager`

```python
settings_manager: SettingsManager[RunContextSettings]
```

### `kiarina.agi.cost_record`

```python
from kiarina.agi.cost_record import (
    CostKind,
    CostRecord,
    CostSource,
    Microdollars,
)
```

#### `CostRecord`

```python
class CostRecord(BaseModel):
    microdollars: Microdollars = 0
    kind: CostKind
    source: CostSource
    metadata: dict[str, Any] = {}
    created_at: datetime = <current UTC time>
```

#### Supporting types

```python
CostKind = Literal[
    "asr",
    "chat",
    "deep_research",
    "image",
    "text_embedding",
    "image_embedding",
    "tts",
    "video",
    "web_search",
] | str
CostSource: TypeAlias = str
Microdollars: TypeAlias = int
```

### `kiarina.agi.cost_logger`

```python
from kiarina.agi.cost_logger import (
    BaseCostLogger,
    CostLogger,
    CostLoggerName,
    CostLoggerSettings,
    CostLoggerSpecifier,
    cost_logger_registry,
    settings_manager,
)
```

#### `BaseCostLogger`

```python
class BaseCostLogger(CostLogger):
    def __init__(self) -> None: ...

    @property
    def name(self) -> CostLoggerName: ...

    @name.setter
    def name(self, value: CostLoggerName) -> None: ...

    @property
    def currency(self) -> CurrencyCode | None: ...

    @property
    def exchange_rate(self) -> float | None: ...

    @property
    def decimal_places(self) -> int | None: ...

    def log_cost_add(self, cost_record: CostRecord) -> None: ...
    def log_cost_flush(self, cost_records: list[CostRecord]) -> None: ...
```

Custom logger 実装用の基底クラスです。

#### `CostLogger`

```python
@runtime_checkable
class CostLogger(Protocol):
    name: CostLoggerName

    def log_cost_add(self, cost_record: CostRecord) -> None: ...
    def log_cost_flush(self, cost_records: list[CostRecord]) -> None: ...
```

#### `CostLoggerSettings`

```python
class CostLoggerSettings(BaseSettings):
    default: CostLoggerSpecifier = "null"
    presets: dict[CostLoggerName, ImportPath] = {
        "console": "kiarina.agi.cost_logger_impl.console:ConsoleCostLogger",
        "null": "kiarina.agi.cost_logger_impl.null:NullCostLogger",
    }
    customs: dict[CostLoggerName, ImportPath] = {}
    currency: CurrencyCode | None = None
    exchange_rate: float | None = None
    decimal_places: int | None = None
```

環境変数 prefix は `KIARINA_AGI_COST_LOGGER_` です。

#### Supporting types and instances

```python
CostLoggerName: TypeAlias = str
CostLoggerSpecifier: TypeAlias = CostLoggerName | str
cost_logger_registry: ComponentRegistry[CostLogger]
settings_manager: SettingsManager[CostLoggerSettings]
```

Specifier は `"{CostLoggerName}?{ConfigString}"` 形式も受け付けます。

### `kiarina.agi.cost_logger_impl.console`

```python
from kiarina.agi.cost_logger_impl.console import ConsoleCostLogger
```

#### `ConsoleCostLogger`

```python
class ConsoleCostLogger(BaseCostLogger):
    def __init__(self) -> None: ...
    def log_cost_add(self, cost_record: CostRecord) -> None: ...
    def log_cost_flush(self, cost_records: list[CostRecord]) -> None: ...
```

### `kiarina.agi.cost_logger_impl.null`

```python
from kiarina.agi.cost_logger_impl.null import NullCostLogger
```

#### `NullCostLogger`

```python
class NullCostLogger(BaseCostLogger):
    def __init__(self) -> None: ...
```

### `kiarina.agi.cost_recorder`

```python
from kiarina.agi.cost_recorder import (
    BaseCostRecorder,
    CostRecorder,
    CostRecorderName,
    CostRecorderSettings,
    CostRecorderSpecifier,
    cost_recorder_registry,
    settings_manager,
)
```

#### `BaseCostRecorder`

```python
class BaseCostRecorder(CostRecorder):
    def __init__(self, **kwargs: Any) -> None: ...

    @property
    def name(self) -> CostRecorderName: ...

    @name.setter
    def name(self, value: CostRecorderName) -> None: ...

    @property
    def total_microdollars(self) -> int: ...

    @property
    def total_dollars(self) -> float: ...

    @property
    def logger(self) -> CostLogger: ...

    def add(self, cost_record: CostRecord) -> None: ...
    def clear(self) -> None: ...
    async def flush(self, run_context: RunContext) -> None: ...
```

`flush` は record を保存し、cost logger に通知してから、保持している record を削除します。

#### `CostRecorder`

```python
@runtime_checkable
class CostRecorder(Protocol):
    name: CostRecorderName
    records: list[CostRecord]

    @property
    def total_microdollars(self) -> int: ...

    @property
    def total_dollars(self) -> float: ...

    def add(self, cost_record: CostRecord) -> None: ...
    def clear(self) -> None: ...
    async def flush(self, run_context: RunContext) -> None: ...
```

#### `CostRecorderSettings`

```python
class CostRecorderSettings(BaseSettings):
    default: CostRecorderSpecifier = "null"
    presets: dict[CostRecorderName, ImportPath] = {
        "local": "kiarina.agi.cost_recorder_impl.local:LocalCostRecorder",
        "null": "kiarina.agi.cost_recorder_impl.null:NullCostRecorder",
    }
    customs: dict[CostRecorderName, ImportPath] = {}
```

環境変数 prefix は `KIARINA_AGI_COST_RECORDER_` です。

#### Supporting types and instances

```python
CostRecorderName: TypeAlias = str
CostRecorderSpecifier: TypeAlias = CostRecorderName | str
cost_recorder_registry: ComponentRegistry[CostRecorder]
settings_manager: SettingsManager[CostRecorderSettings]
```

Specifier は `"{CostRecorderName}?{ConfigString}"` 形式も受け付けます。

### `kiarina.agi.cost_recorder_impl.local`

```python
from kiarina.agi.cost_recorder_impl.local import LocalCostRecorder
```

#### `LocalCostRecorder`

```python
class LocalCostRecorder(BaseCostRecorder):
    def __init__(self, **kwargs: Any) -> None: ...

    @property
    def file_path(self) -> str: ...
```

### `kiarina.agi.cost_recorder_impl.null`

```python
from kiarina.agi.cost_recorder_impl.null import NullCostRecorder
```

#### `NullCostRecorder`

```python
class NullCostRecorder(BaseCostRecorder):
    def __init__(self, **kwargs: Any) -> None: ...
```

### `kiarina.agi.request_logger`

```python
from kiarina.agi.request_logger import (
    BaseRequestLogger,
    RequestLogEntry,
    RequestLogger,
    RequestLoggerName,
    RequestLoggerSettings,
    RequestLoggerSpecifier,
    request_logger_registry,
    settings_manager,
)
```

#### `BaseRequestLogger`

```python
class BaseRequestLogger(RequestLogger):
    def __init__(self, **kwargs: Any) -> None: ...

    @property
    def name(self) -> RequestLoggerName: ...

    @name.setter
    def name(self, value: RequestLoggerName) -> None: ...

    async def log_request_success(
        self,
        log_entry: RequestLogEntry,
        *,
        run_context: RunContext,
    ) -> None: ...

    async def log_request_error(
        self,
        log_entry: RequestLogEntry,
        error: Exception,
        *,
        run_context: RunContext,
    ) -> None: ...
```

#### `RequestLogEntry`

```python
class RequestLogEntry(BaseModel):
    kind: str
    source: str
    content: str
    metadata: dict[str, Any] = {}
    created_at: datetime = <current UTC time>
```

#### `RequestLogger`

```python
@runtime_checkable
class RequestLogger(Protocol):
    name: RequestLoggerName

    async def log_request_success(
        self,
        log_entry: RequestLogEntry,
        *,
        run_context: RunContext,
    ) -> None: ...

    async def log_request_error(
        self,
        log_entry: RequestLogEntry,
        error: Exception,
        *,
        run_context: RunContext,
    ) -> None: ...
```

#### `RequestLoggerSettings`

```python
class RequestLoggerSettings(BaseSettings):
    default: RequestLoggerSpecifier = "null"
    presets: dict[RequestLoggerName, ImportPath] = {
        "console": "kiarina.agi.request_logger_impl.console:ConsoleRequestLogger",
        "local": "kiarina.agi.request_logger_impl.local:LocalRequestLogger",
        "null": "kiarina.agi.request_logger_impl.null:NullRequestLogger",
    }
    customs: dict[RequestLoggerName, ImportPath] = {}
```

環境変数 prefix は `KIARINA_AGI_REQUEST_LOGGER_` です。

#### Supporting types and instances

```python
RequestLoggerName: TypeAlias = str
RequestLoggerSpecifier: TypeAlias = RequestLoggerName | str
request_logger_registry: ComponentRegistry[RequestLogger]
settings_manager: SettingsManager[RequestLoggerSettings]
```

Specifier は `"{RequestLoggerName}?{ConfigString}"` 形式も受け付けます。

### `kiarina.agi.request_logger_impl.console`

```python
from kiarina.agi.request_logger_impl.console import ConsoleRequestLogger
```

#### `ConsoleRequestLogger`

```python
class ConsoleRequestLogger(BaseRequestLogger):
    def __init__(self, **kwargs: Any) -> None: ...

    async def log_request_success(
        self,
        log_entry: RequestLogEntry,
        *,
        run_context: RunContext,
    ) -> None: ...

    async def log_request_error(
        self,
        log_entry: RequestLogEntry,
        error: Exception,
        *,
        run_context: RunContext,
    ) -> None: ...
```

### `kiarina.agi.request_logger_impl.local`

```python
from kiarina.agi.request_logger_impl.local import LocalRequestLogger
```

#### `LocalRequestLogger`

```python
class LocalRequestLogger(BaseRequestLogger):
    def __init__(self, **kwargs: Any) -> None: ...

    async def log_request_success(
        self,
        log_entry: RequestLogEntry,
        *,
        run_context: RunContext,
    ) -> None: ...

    async def log_request_error(
        self,
        log_entry: RequestLogEntry,
        error: Exception,
        *,
        run_context: RunContext,
    ) -> None: ...
```

### `kiarina.agi.request_logger_impl.null`

```python
from kiarina.agi.request_logger_impl.null import NullRequestLogger
```

#### `NullRequestLogger`

```python
class NullRequestLogger(BaseRequestLogger):
    def __init__(self, **kwargs: Any) -> None: ...
```

### `kiarina.agi.token_utils`

```python
from kiarina.agi.token_utils import (
    ImageSize,
    TokenCount,
    TokenUtilsSettings,
    calc_audio_token,
    calc_image_token,
    calc_pdf_token,
    calc_text_token,
    calc_video_token,
    settings_manager,
)
```

#### Token calculation

```python
def calc_audio_token(duration: float) -> TokenCount: ...
def calc_image_token(image_size: ImageSize) -> TokenCount: ...
def calc_pdf_token(text: str, image_sizes: list[ImageSize]) -> int: ...
def calc_text_token(text: str) -> TokenCount: ...
def calc_video_token(duration: float) -> TokenCount: ...
```

`duration` の単位は秒です。`calc_pdf_token` は text と各 page image の見積もりを合計します。

#### `TokenUtilsSettings`

```python
class TokenUtilsSettings(BaseSettings):
    tiktoken_model_name: str = "gpt-4o"
```

環境変数 prefix は `KIARINA_AGI_TOKEN_UTILS_` です。

#### Supporting types and instances

```python
class ImageSize(NamedTuple):
    width: int
    height: int

TokenCount: TypeAlias = int
settings_manager: SettingsManager[TokenUtilsSettings]
```

### `kiarina.agi.console_utils`

```python
from kiarina.agi.console_utils import (
    ConsoleColor,
    divider,
    format_run_context,
    section_header,
    stderr_color,
)
```

#### Console formatting

```python
def divider(width: int = 80, fill_char: str = "-") -> str: ...
def format_run_context(run_context: RunContext) -> str: ...
def section_header(
    title: str,
    *,
    width: int = 80,
    fill_char: str = "-",
) -> str: ...

@contextmanager
def stderr_color(color: ConsoleColor) -> Iterator[None]: ...
```

`stderr_color` は stderr が TTY の場合だけ ANSI color を適用します。

#### `ConsoleColor`

```python
ConsoleColor = Literal[
    "black",
    "red",
    "green",
    "yellow",
    "blue",
    "magenta",
    "cyan",
    "white",
]
```

### `kiarina.agi.cost_utils`

```python
from kiarina.agi.cost_utils import format_cost
```

#### `format_cost`

```python
def format_cost(
    microdollars: int,
    *,
    currency: CurrencyCode | None = None,
    exchange_rate: float | None = None,
    decimal_places: int | None = None,
) -> str: ...
```

Microdollars を通貨付き文字列へ変換します。USD 以外へ変換する場合は `currency` と `exchange_rate` の両方を指定します。

### `kiarina.agi.file_utils`

```python
from kiarina.agi.file_utils import (
    format_xml_attributes,
    is_uri,
    normalize_line_number,
    normalize_page,
    normalize_time,
)
```

#### File reference formatting

```python
def format_xml_attributes(xml_attributes: dict[str, Any]) -> str: ...
def is_uri(s: str) -> bool: ...
def normalize_line_number(line_number: int, line_count: int) -> int: ...
def normalize_page(page_number: int, page_count: int) -> int: ...
def normalize_time(time: float, duration: float) -> float: ...
```

`normalize_line_number` と `normalize_page` は 1 始まりの値を有効範囲に収めます。`normalize_time` は秒単位の値を `0` から `duration` の範囲に収めます。

### `kiarina.agi.image_types`

```python
from kiarina.agi.image_types import ImagePixels
```

#### `ImagePixels`

```python
ImagePixels: TypeAlias = UInt8[np.ndarray, "height width rgb"]
```

`uint8` の RGB image array を表します。
