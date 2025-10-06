# kiarina-lib-google

A Python client library for Google Cloud services with configuration management.

## Features

- **Configuration Management**: Use `pydantic-settings-manager` for flexible configuration
- **Type Safety**: Full type hints and Pydantic validation
- **Sync & Async**: Support for both synchronous and asynchronous operations

## Installation

```bash
pip install kiarina-lib-google
```

## Quick Start

```python
from kiarina.lib.google import __version__

print(f"kiarina-lib-google version: {__version__}")
```

## Development

### Prerequisites

- Python 3.12+

### Setup

```bash
# Clone the repository
git clone https://github.com/kiarina/kiarina-python.git
cd kiarina-python

# Setup development environment
mise run setup
```

### Running Tests

```bash
# Run format, lint, type checks and tests
mise run package kiarina-lib-google

# Coverage report
mise run package:test kiarina-lib-google --coverage
```

## Dependencies

- [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) - Settings management
- [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) - Advanced settings management

## License

This project is licensed under the MIT License - see the [LICENSE](../../LICENSE) file for details.

## Contributing

This is a personal project, but contributions are welcome! Please feel free to submit issues or pull requests.

## Related Projects

- [kiarina-python](https://github.com/kiarina/kiarina-python) - The main monorepo containing this package
- [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) - Configuration management library used by this package
