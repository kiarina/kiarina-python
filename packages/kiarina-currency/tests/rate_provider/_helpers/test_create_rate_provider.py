import pytest

from kiarina.currency.rate_provider import (
    BaseRateProvider,
    create_rate_provider,
    settings_manager,
)


def dummy(**kwargs) -> object:
    return object()


class RateProvider(BaseRateProvider):
    async def get_rate(
        self,
        from_currency: str,
        to_currency: str,
        *,
        default: float | None = None,
    ) -> float:
        return 1.23


@pytest.fixture(autouse=True)
def setup():
    settings_manager.cli_args = {
        "default": "test",
        "providers": {"test": __name__},
    }
    yield
    settings_manager.cli_args = {}


def test_invalid_provider() -> None:
    with pytest.raises(TypeError, match="is not a valid RateProvider"):
        create_rate_provider(__name__ + ":dummy")


def test_default() -> None:
    provider = create_rate_provider()
    assert isinstance(provider, RateProvider)


def test_rate_provider_name() -> None:
    provider = create_rate_provider("test")
    assert isinstance(provider, RateProvider)


def test_import_path() -> None:
    provider = create_rate_provider(__name__)
    assert isinstance(provider, RateProvider)
