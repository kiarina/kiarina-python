import pytest

from kiarina.lib.google import GoogleSettings, get_genai_http_options


@pytest.fixture(autouse=True)
def clear_genai_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GOOGLE_GENAI_USE_ENTERPRISE", raising=False)
    monkeypatch.delenv("GOOGLE_GENAI_USE_VERTEXAI", raising=False)


def test_developer_api_pins_api_version() -> None:
    options = get_genai_http_options(
        settings=GoogleSettings(), client_options={"api_key": "key"}, timeout=1000
    )

    assert options == {"timeout": 1000, "api_version": "v1beta"}


def test_vertexai_keeps_sdk_default() -> None:
    options = get_genai_http_options(
        settings=GoogleSettings(), client_options={"vertexai": True}
    )

    assert options == {}


def test_vertexai_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GOOGLE_GENAI_USE_VERTEXAI", "true")

    options = get_genai_http_options(settings=GoogleSettings(), client_options={})

    assert options == {}


def test_enterprise_variable_wins(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GOOGLE_GENAI_USE_ENTERPRISE", "false")
    monkeypatch.setenv("GOOGLE_GENAI_USE_VERTEXAI", "true")

    options = get_genai_http_options(settings=GoogleSettings(), client_options={})

    assert options == {"api_version": "v1beta"}


def test_none_uses_sdk_default() -> None:
    options = get_genai_http_options(
        settings=GoogleSettings(gemini_api_version=None), client_options={}
    )

    assert options == {}
