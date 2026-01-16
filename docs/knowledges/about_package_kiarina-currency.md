---
title: About kiarina-currency package
description: >-
  kiarina-currency is a currency utilities library
  with exchange rate support and pluggable rate provider system.
---

kiarina-currency provides currency code types and exchange rate retrieval with a pluggable rate provider architecture.
This library focuses on simplicity and flexibility, allowing you to choose between static configuration-based rates or real-time API-based rates.

Key features include:
- System currency detection from locale settings
- Exchange rate retrieval with pluggable rate providers
- Built-in static rate provider with configurable exchange rates
- Built-in Frankfurter API provider for real-time rates
- Support for direct, inverted, and indirect rate calculations
- Custom rate provider support via plugin pattern
- Configuration management using pydantic-settings-manager
- Type-safe with full type hints

Main utilities:
- `get_system_currency()`: Detect system currency from locale settings (e.g., "JPY" on Japanese systems)
- `get_exchange_rate()`: Retrieve exchange rates between currencies
- `create_rate_provider()`: Factory function for creating rate providers
- `BaseRateProvider`: Abstract base class for custom rate providers

Rate providers:
- **Static provider** (default): Configuration-based static rates with support for direct, inverted, and indirect calculations
- **Frankfurter provider**: Real-time rates from the free Frankfurter API (European Central Bank data)
- **Custom providers**: Implement `BaseRateProvider` for your own rate sources
