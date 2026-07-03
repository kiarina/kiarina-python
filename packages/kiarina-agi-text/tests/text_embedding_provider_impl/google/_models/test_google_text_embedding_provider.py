# mypy: ignore-errors

from pathlib import Path

import numpy as np
import pytest
from pydantic_settings_manager import clear_user_configs, load_user_configs

from kiarina.agi.text_embedding_provider_impl.google import (
    GoogleTextEmbeddingProvider,
    GoogleTextEmbeddingProviderSettings,
)
from kiarina.utils.file import read_yaml_dict


@pytest.fixture(autouse=True)
def test_settings():
    settings_path = (
        Path(__file__).resolve().parents[3]
        / "chat_provider_impl"
        / "lc_google_genai"
        / "test_settings.yaml"
    )
    user_configs = read_yaml_dict(settings_path)

    if not user_configs:
        pytest.skip(f"test_settings.yaml is empty: {settings_path}")

    load_user_configs(user_configs)
    yield
    clear_user_configs(user_configs)


@pytest.fixture
def provider() -> GoogleTextEmbeddingProvider:
    provider = GoogleTextEmbeddingProvider(
        GoogleTextEmbeddingProviderSettings(
            backend_type="gemini_api",
            google_auth_settings_key="api_key",
            model_name="gemini-embedding-2",
            dimension=1536,
        )
    )
    provider.name = "google"
    return provider


def test_properties(provider: GoogleTextEmbeddingProvider) -> None:
    print(f"__str__: {provider}")
    print(f"google_auth_settings: {provider.google_auth_settings}")
    print(f"backend_config: {provider.backend_config}")

    space = provider.get_space()
    assert space.kind == "text"
    assert space.dimension == 1536


@pytest.mark.costly
async def test_embed_text_request(
    provider: GoogleTextEmbeddingProvider,
    cost_recorder,
    run_context,
) -> None:
    embedding = await provider.embed(
        "Hello, world!",
        cost_recorder=cost_recorder,
        run_context=run_context,
    )

    assert embedding.kind == "text"
    assert embedding.space_id == provider.get_space().space_id
    assert len(embedding.vector) == 1536
    assert np.isfinite(embedding.to_numpy()).all()
    assert embedding.metadata["model_name"] == "gemini-embedding-2"
