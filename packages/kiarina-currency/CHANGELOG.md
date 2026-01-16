# Changelog

All notable changes to the kiarina-currency package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of kiarina-currency package
- `CurrencyCode` type alias for ISO 4217 currency codes
- `get_exchange_rate()` async function for retrieving exchange rates
- `RateProvider` protocol for pluggable rate provider implementations
- `BaseRateProvider` abstract base class for custom providers
- `create_rate_provider()` factory function with plugin pattern support
- Static rate provider with configurable exchange rates
  - Direct rate lookup
  - Inverted rate calculation
  - Indirect rate calculation via base currency
  - Default rates from USD to 11 major currencies (JPY, EUR, GBP, CNY, KRW, AUD, CAD, CHF, HKD, SGD, INR)
- Frankfurter API rate provider for real-time exchange rates
  - HTTP client with timeout and error handling
  - Default value fallback for unsupported currencies or network errors
- `CurrencyError` and `ExchangeRateNotFoundError` exception classes
- Configuration management with pydantic-settings-manager
- Comprehensive test suite with 100% coverage
- Full type hints and py.typed support
