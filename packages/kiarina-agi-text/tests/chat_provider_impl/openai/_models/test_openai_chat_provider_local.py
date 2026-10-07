"""
Tests against a local OpenAI-compatible server (kiapi).

Put `kiarina.lib.openai` settings with a `local` config in
`tests/chat_provider_impl/openai/test_settings.yaml`.
"""

from collections.abc import Iterator
from pathlib import Path

import pytest
from pydantic_settings_manager import clear_user_configs, load_user_configs

from kiarina.agi.chat_model import settings_manager as chat_model_settings_manager
from kiarina.agi.chat_provider_impl.openai import (
    OpenAIChatProvider,
    OpenAIChatProviderSettings,
)
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.file_info import ImageFileInfo
from kiarina.agi.message import HumanMessage
from kiarina.agi.run_context import RunContext
from kiarina.utils.file import read_yaml_dict


@pytest.fixture
def setup_settings() -> Iterator[None]:
    settings_path = Path(__file__).resolve().parents[1] / "test_settings.yaml"

    if not settings_path.is_file():
        pytest.skip(f"test_settings.yaml does not exist: {settings_path}")

    user_configs = read_yaml_dict(settings_path)

    if not user_configs:
        pytest.skip(f"test_settings.yaml is empty: {settings_path}")

    load_user_configs(user_configs)
    yield
    clear_user_configs(user_configs)


@pytest.fixture
def local_provider(setup_settings: None) -> OpenAIChatProvider:
    import httpx

    config = chat_model_settings_manager.settings.presets["qwen3.8-flash-next-fast"]
    provider = OpenAIChatProvider(
        OpenAIChatProviderSettings.model_validate(config.provider_config)
    )
    provider.name = "openai"

    base_url = str(provider.client.base_url).rstrip("/").removesuffix("/v1")

    try:
        httpx.get(f"{base_url}/health", timeout=2.0).raise_for_status()
    except Exception as exc:
        pytest.skip(f"Local server is not healthy: {base_url} ({exc})")

    return provider


@pytest.mark.parametrize("streaming", [False, True])
async def test_image(
    local_provider: OpenAIChatProvider,
    image_file_info: ImageFileInfo,
    streaming: bool,
    cost_recorder: CostRecorder,
    run_context: RunContext,
) -> None:
    ai_messages = [
        ai_message
        async for ai_message in local_provider.run(
            [
                HumanMessage.create(
                    "What is in this image? One sentence.", [image_file_info]
                )
            ],
            streaming=streaming,
            cost_recorder=cost_recorder,
            run_context=run_context,
        )
    ]

    print(ai_messages[-1].to_text())

    assert ai_messages[-1].type == "ai"
    assert ai_messages[-1].to_text()
