# kiarina-currency

[![PyPI](https://img.shields.io/pypi/v/kiarina-currency.svg)](https://pypi.org/project/kiarina-currency/)
[![Python](https://img.shields.io/pypi/pyversions/kiarina-currency.svg)](https://pypi.org/project/kiarina-currency/)
[![License](https://img.shields.io/pypi/l/kiarina-currency.svg)](../../LICENSE)

English | [日本語](README.ja.md)

> [!NOTE]
> Provides system currency detection and exchange rate retrieval through pluggable providers.

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

- **Detect the system currency**
  Resolve an ISO 4217 currency code from locale settings and environment variables.
- **Get exchange rates**
  Retrieve rates from configured static data or the Frankfurter API.
- **Extend rate providers**
  Select an implementation by provider instance, registered name, or import path.

### Detecting the System Currency

```python
from kiarina.currency import get_system_currency

currency = get_system_currency()
```

Detection checks `locale.localeconv()`, the locale name, `LC_ALL`, `LC_MONETARY`, and `LANG`. It returns `"USD"` when detection fails.

### Getting Exchange Rates

The static provider is used by default.

```python
from kiarina.currency import get_exchange_rate

rate = await get_exchange_rate("USD", "JPY")
```

The static provider resolves direct rates, inverted rates, and indirect rates through the base currency, in that order. A fallback value can be provided when a rate is unavailable.

```python
rate = await get_exchange_rate("USD", "XXX", default=1.0)
```

The Frankfurter provider retrieves rates from the [Frankfurter API](https://www.frankfurter.app/).

```python
rate = await get_exchange_rate(
    "USD",
    "EUR",
    rate_options={"rate_provider": "frankfurter"},
)
```

### Configuring Providers

Settings are managed by `pydantic-settings-manager`. For example, static rates can be configured at runtime.

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

Environment variable names combine each settings class prefix with its field name.

| Setting | Environment Variable |
| --- | --- |
| Default provider | `KIARINA_CURRENCY_RATE_PROVIDER_DEFAULT` |
| Static provider base currency | `KIARINA_CURRENCY_RATE_PROVIDER_IMPL_STATIC_BASE_CURRENCY` |
| Frankfurter API base URL | `KIARINA_CURRENCY_RATE_PROVIDER_IMPL_FRANKFURTER_BASE_URL` |
| Frankfurter API timeout | `KIARINA_CURRENCY_RATE_PROVIDER_IMPL_FRANKFURTER_TIMEOUT` |

### Creating a Custom Provider

An instance implementing the `RateProvider` protocol can be passed directly.

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

A provider can also be created from a registered name or import path.

```python
from kiarina.currency import create_rate_provider

provider = create_rate_provider("my_package.providers:CustomRateProvider")
```

When an import path omits the class name, `:RateProvider` is appended.

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

`get_system_currency` returns the system currency and falls back to `"USD"` when detection fails.

`get_exchange_rate` retrieves a rate from the selected provider. It raises `ExchangeRateNotFoundError` when the rate is unavailable and no `default` is provided.

`create_rate_provider` creates a provider from a registered name or import path. It raises `TypeError` when the resulting object does not implement `RateProvider`.

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

`rate_provider_settings_manager` is an alias for `kiarina.currency.rate_provider.settings_manager`.

#### Types

```python
CurrencyCode: TypeAlias = str
RateProviderName: TypeAlias = str

class RateOptions(TypedDict, total=False):
    rate_provider: RateProvider | RateProviderName | ImportPath | None
```

`CurrencyCode` represents an ISO 4217 currency code. `RateOptions.rate_provider` accepts a provider instance, registered name, import path, or `None`.

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

Use this base class for custom providers and implement `get_rate`.

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

`rates` is nested by source currency, target currency, and rate.

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

When an HTTP error, network error, timeout, or missing rate occurs, the provider returns `default` when supplied. Otherwise, it raises `ExchangeRateNotFoundError`.

#### Settings

```python
class FrankfurterRateProviderSettings(BaseSettings):
    base_url: str = "https://api.frankfurter.app"
    timeout: float = 10.0

settings_manager: SettingsManager[FrankfurterRateProviderSettings]
```
