import pytest
from pydantic import SecretStr

from kiarina.lib.google import GoogleSettings, get_genai_options


def test_vertex_ai_api_key_express_mode() -> None:
    settings = GoogleSettings(
        type="api_key",
        api_key=SecretStr("test-api-key"),
        project_id="test-project",
        location="us-central1",
        vertexai=True,
    )

    options = get_genai_options(settings=settings)

    assert options == {
        "vertexai": True,
        "api_key": "test-api-key",
    }


def test_vertex_ai_credentials_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    credentials = object()

    def fake_get_credentials(**kwargs: object) -> object:
        settings = kwargs["settings"]
        assert isinstance(settings, GoogleSettings)
        assert settings.type == "service_account"
        assert kwargs["scopes"] == ["https://www.googleapis.com/auth/cloud-platform"]
        return credentials

    monkeypatch.setattr(
        "kiarina.lib.google._helpers.get_genai_options.get_credentials",
        fake_get_credentials,
    )

    settings = GoogleSettings(
        type="service_account",
        project_id="test-project",
        location="us-central1",
        vertexai=True,
    )

    options = get_genai_options(
        settings=settings,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )

    assert options == {
        "vertexai": True,
        "credentials": credentials,
        "project": "test-project",
        "location": "us-central1",
    }


def test_gemini_developer_api_mode() -> None:
    settings = GoogleSettings(
        type="api_key",
        api_key=SecretStr("test-api-key"),
        vertexai=False,
    )

    options = get_genai_options(settings=settings)

    assert options == {"api_key": "test-api-key"}


def test_default_api_key_uses_gemini_developer_api_mode() -> None:
    settings = GoogleSettings(
        type="api_key",
        api_key=SecretStr("test-api-key"),
    )

    options = get_genai_options(settings=settings)

    assert options == {"api_key": "test-api-key"}


def test_default_credentials_uses_vertex_ai_credentials_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    credentials = object()

    def fake_get_credentials(**kwargs: object) -> object:
        settings = kwargs["settings"]
        assert isinstance(settings, GoogleSettings)
        assert settings.type == "default"
        return credentials

    monkeypatch.setattr(
        "kiarina.lib.google._helpers.get_genai_options.get_credentials",
        fake_get_credentials,
    )

    settings = GoogleSettings(
        type="default",
        project_id="test-project",
        location="us-central1",
    )

    options = get_genai_options(settings=settings)

    assert options == {
        "vertexai": True,
        "credentials": credentials,
        "project": "test-project",
        "location": "us-central1",
    }
