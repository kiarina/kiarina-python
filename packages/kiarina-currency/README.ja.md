# kiarina-currency

[English](README.md) | 日本語

kiarina namespace 向けの、為替レート対応つき通貨ユーティリティです。

## Purpose

通貨コード型と、差し替え可能な rate provider による為替レート取得機能を提供します。

## Installation

```bash
pip install kiarina-currency
```

## Quick Start

### Basic Usage

```python
from kiarina.currency import get_exchange_rate, get_system_currency

currency = get_system_currency()
print(f"System currency: {currency}")

rate = await get_exchange_rate("USD", "JPY")
print(f"1 USD = {rate} JPY")

rate = await get_exchange_rate("USD", "XXX", default=1.0)
```

### Using Different Rate Providers

```python
from kiarina.currency import get_exchange_rate

rate = await get_exchange_rate(
    "USD",
    "EUR",
    rate_options={"rate_provider": "frankfurter"},
)
```

### Custom Rate Provider

```python
from kiarina.currency import BaseRateProvider, get_exchange_rate


class MyRateProvider(BaseRateProvider):
    async def get_rate(
        self,
        from_currency: str,
        to_currency: str,
        *,
        default: float | None = None,
    ) -> float:
        return 1.5


rate = await get_exchange_rate(
    "USD",
    "EUR",
    rate_options={"rate_provider": MyRateProvider()},
)
```

## API Reference

### `get_system_currency()`

システムの locale 設定から ISO 4217 の通貨コードを取得します。検出できない場合は `"USD"` にフォールバックします。

### `get_exchange_rate()`

2 つの通貨間の為替レートを取得します。レートが見つからず `default` も指定されていない場合は `ExchangeRateNotFoundError` を送出します。

### Rate Providers

#### Built-in Providers

- **`static`**: 設定ベースの静的レート provider です。直接レート、逆レート、基準通貨経由の間接レートを解決します。
- **`frankfurter`**: [Frankfurter API](https://www.frankfurter.app/) から日次更新の為替レートを取得します。

#### Creating Custom Providers

独自 provider は `BaseRateProvider` を継承し、`get_rate()` を実装して作成します。

## Configuration

### Static Rate Provider

```yaml
kiarina.currency.rate_provider_impl.static:
  base_currency: "USD"
  rates:
    USD:
      JPY: 158.27
      EUR: 0.86
```

### Frankfurter Rate Provider

```yaml
kiarina.currency.rate_provider_impl.frankfurter:
  base_url: "https://api.frankfurter.app"
  timeout: 10.0
```

### Rate Provider Selection

```yaml
kiarina.currency.rate_provider:
  default: "static"
  providers:
    static: "kiarina.currency.rate_provider_impl.static:StaticRateProvider"
    frankfurter: "kiarina.currency.rate_provider_impl.frankfurter:FrankfurterRateProvider"
```

## Testing

```bash
mise run package:test kiarina-currency

export KIARINA_CURRENCY_RATE_PROVIDER_IMPL_FRANKFURTER_TEST_ENABLED=1
mise run package:test kiarina-currency
```

## Dependencies

- `httpx`
- `kiarina-utils-common`
- `pydantic`
- `pydantic-settings`
- `pydantic-settings-manager`

## License

このプロジェクトは MIT License のもとで公開されています。詳細は [LICENSE](../../LICENSE) を参照してください。

## Related Projects

- [kiarina-python](https://github.com/kiarina/kiarina-python)
- [Frankfurter API](https://www.frankfurter.app/)

