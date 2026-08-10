# kiarina-currency

[![PyPI](https://img.shields.io/pypi/v/kiarina-currency.svg)](https://pypi.org/project/kiarina-currency/)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-currency.svg)](https://pypi.org/project/kiarina-currency/)
[![License](https://img.shields.io/pypi/l/kiarina-currency.svg)](../../LICENSE)

[English](README.md) | 日本語

> [!NOTE]
> システム通貨の検出と、差し替え可能な provider による為替レート取得を提供します。

## Dependencies

| Package | Version | License |
| --- | --- | --- |
| [HTTPX](https://github.com/encode/httpx) | `>=0.28.1` | [BSD-3-Clause](https://github.com/encode/httpx/blob/master/LICENSE.md) |
| [kiarina-utils-common](../kiarina-utils-common/) | `>=1.11.0` | [MIT](../../LICENSE) |
| [Pydantic](https://github.com/pydantic/pydantic) | `>=2.10.6` | [MIT](https://github.com/pydantic/pydantic/blob/main/LICENSE) |
| [pydantic-settings](https://github.com/pydantic/pydantic-settings) | `>=2.7.1` | [MIT](https://github.com/pydantic/pydantic-settings/blob/main/LICENSE) |
| [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) | `>=3.2.0` | [MIT](https://github.com/kiarina/pydantic-settings-manager/blob/main/LICENSE) |

## Installation

```bash
pip install kiarina-currency
```

## Features

- **システム通貨の検出**
  locale と環境変数から ISO 4217 通貨コードを取得します。
- **為替レートの取得**
  静的レートまたは Frankfurter API を利用してレートを取得します。
- **rate provider の拡張**
  provider インスタンス、登録名、import path のいずれかで実装を選択できます。

### Detecting the System Currency

```python
from kiarina.currency import get_system_currency

currency = get_system_currency()
```

`locale.localeconv()`、locale 名、`LC_ALL`、`LC_MONETARY`、`LANG` の順に通貨を検出します。検出できない場合は `"USD"` を返します。

### Getting Exchange Rates

既定では静的 provider を使用します。

```python
from kiarina.currency import get_exchange_rate

rate = await get_exchange_rate("USD", "JPY")
```

静的 provider は、直接レート、逆レート、基準通貨を経由する間接レートをこの順に解決します。レートが存在しない場合の値も指定できます。

```python
rate = await get_exchange_rate("USD", "XXX", default=1.0)
```

Frankfurter provider は [Frankfurter API](https://www.frankfurter.app/) からレートを取得します。

```python
rate = await get_exchange_rate(
    "USD",
    "EUR",
    rate_options={"rate_provider": "frankfurter"},
)
```

### Configuring Providers

設定は `pydantic-settings-manager` で管理されます。たとえば、静的レートを実行時に設定できます。

```python
from kiarina.currency import get_exchange_rate
from kiarina.currency.rate_provider_impl.static import settings_manager

settings_manager.cli_args = {
    "base_currency": "USD",
    "rates": {
        "USD": {
            "EUR": 0.85,
            "JPY": 150.0,
        },
    },
}

rate = await get_exchange_rate("JPY", "EUR")
```

環境変数では、各設定クラスの prefix とフィールド名を組み合わせます。

| Setting | Environment Variable |
| --- | --- |
| 既定の provider | `KIARINA_CURRENCY_RATE_PROVIDER_DEFAULT` |
| 静的 provider の基準通貨 | `KIARINA_CURRENCY_RATE_PROVIDER_IMPL_STATIC_BASE_CURRENCY` |
| Frankfurter API の base URL | `KIARINA_CURRENCY_RATE_PROVIDER_IMPL_FRANKFURTER_BASE_URL` |
| Frankfurter API の timeout | `KIARINA_CURRENCY_RATE_PROVIDER_IMPL_FRANKFURTER_TIMEOUT` |

### Creating a Custom Provider

`RateProvider` protocol を実装したインスタンスを直接渡せます。

```python
from kiarina.currency import CurrencyCode, get_exchange_rate
from kiarina.currency.rate_provider import BaseRateProvider


class CustomRateProvider(BaseRateProvider):
    async def get_rate(
        self,
        from_currency: CurrencyCode,
        to_currency: CurrencyCode,
        *,
        default: float | None = None,
    ) -> float:
        return 1.5


rate = await get_exchange_rate(
    "USD",
    "EUR",
    rate_options={"rate_provider": CustomRateProvider()},
)
```

登録名または import path から provider を生成することもできます。

```python
from kiarina.currency import create_rate_provider

provider = create_rate_provider("my_package.providers:CustomRateProvider")
```

クラス名を省略した import path には `:RateProvider` が補われます。

## API Reference

### `kiarina.currency`

```python
from kiarina.currency import (
    CurrencyCode,
    CurrencyError,
    ExchangeRateNotFoundError,
    RateOptions,
    RateProvider,
    RateProviderName,
    RateProviderSettings,
    create_rate_provider,
    get_exchange_rate,
    get_system_currency,
    rate_provider_settings_manager,
)
```

#### Functions

```python
def get_system_currency() -> CurrencyCode: ...

async def get_exchange_rate(
    from_currency: CurrencyCode,
    to_currency: CurrencyCode,
    *,
    default: float | None = None,
    rate_options: RateOptions | None = None,
) -> float: ...

def create_rate_provider(
    provider_name: RateProviderName | ImportPath | None = None,
    **kwargs: Any,
) -> RateProvider: ...
```

`get_system_currency` はシステム通貨を返し、検出できない場合は `"USD"` にフォールバックします。

`get_exchange_rate` は選択された provider からレートを取得します。レートを取得できず `default` がない場合は `ExchangeRateNotFoundError` を送出します。

`create_rate_provider` は登録名または import path から provider を生成します。生成されたオブジェクトが `RateProvider` を満たさない場合は `TypeError` を送出します。

#### `RateProvider`

```python
@runtime_checkable
class RateProvider(Protocol):
    async def get_rate(
        self,
        from_currency: CurrencyCode,
        to_currency: CurrencyCode,
        *,
        default: float | None = None,
    ) -> float: ...
```

#### Settings

```python
class RateProviderSettings(BaseSettings):
    default: RateProviderName = "static"
    providers: dict[RateProviderName, ImportPath] = {
        "frankfurter": "kiarina.currency.rate_provider_impl.frankfurter:FrankfurterRateProvider",
        "static": "kiarina.currency.rate_provider_impl.static:StaticRateProvider",
    }

rate_provider_settings_manager: SettingsManager[RateProviderSettings]
```

`rate_provider_settings_manager` は `kiarina.currency.rate_provider.settings_manager` の別名です。

#### Types

```python
CurrencyCode: TypeAlias = str
RateProviderName: TypeAlias = str

class RateOptions(TypedDict, total=False):
    rate_provider: RateProvider | RateProviderName | ImportPath | None
```

`CurrencyCode` は ISO 4217 通貨コードを表します。`RateOptions.rate_provider` には provider インスタンス、登録名、import path、または `None` を指定できます。

#### Exceptions

```python
class CurrencyError(Exception): ...

class ExchangeRateNotFoundError(CurrencyError): ...
```

### `kiarina.currency.rate_provider`

```python
from kiarina.currency.rate_provider import (
    BaseRateProvider,
    RateProvider,
    RateProviderName,
    RateProviderSettings,
    create_rate_provider,
    settings_manager,
)
```

#### `BaseRateProvider`

```python
class BaseRateProvider(RateProvider, ABC):
    def __init__(self, **kwargs: Any) -> None: ...

    @abstractmethod
    async def get_rate(
        self,
        from_currency: CurrencyCode,
        to_currency: CurrencyCode,
        *,
        default: float | None = None,
    ) -> float: ...
```

カスタム provider の基底クラスです。`get_rate` を実装してください。

```python
settings_manager: SettingsManager[RateProviderSettings]
```

### `kiarina.currency.rate_provider_impl.static`

```python
from kiarina.currency.rate_provider_impl.static import (
    StaticRateProvider,
    StaticRateProviderSettings,
    settings_manager,
)
```

#### `StaticRateProvider`

```python
class StaticRateProvider(BaseRateProvider):
    async def get_rate(
        self,
        from_currency: CurrencyCode,
        to_currency: CurrencyCode,
        *,
        default: float | None = None,
    ) -> float: ...
```

#### Settings

```python
class StaticRateProviderSettings(BaseSettings):
    base_currency: CurrencyCode = "USD"
    rates: dict[CurrencyCode, dict[CurrencyCode, float]]

settings_manager: SettingsManager[StaticRateProviderSettings]
```

`rates` は source currency、target currency、rate の順でネストします。

### `kiarina.currency.rate_provider_impl.frankfurter`

```python
from kiarina.currency.rate_provider_impl.frankfurter import (
    FrankfurterRateProvider,
    FrankfurterRateProviderSettings,
    settings_manager,
)
```

#### `FrankfurterRateProvider`

```python
class FrankfurterRateProvider(BaseRateProvider):
    async def get_rate(
        self,
        from_currency: CurrencyCode,
        to_currency: CurrencyCode,
        *,
        default: float | None = None,
    ) -> float: ...
```

HTTP error、network error、timeout、またはレスポンスにレートがない場合、`default` が指定されていればその値を返します。指定されていなければ `ExchangeRateNotFoundError` を送出します。

#### Settings

```python
class FrankfurterRateProviderSettings(BaseSettings):
    base_url: str = "https://api.frankfurter.app"
    timeout: float = 10.0

settings_manager: SettingsManager[FrankfurterRateProviderSettings]
```
