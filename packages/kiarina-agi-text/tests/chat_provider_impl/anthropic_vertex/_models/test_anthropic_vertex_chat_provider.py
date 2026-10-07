"""
Vertex AI tests need `kiarina.lib.google` settings with a `project_id` that can call
Claude, in `tests/chat_provider_impl/anthropic_vertex/test_settings.yaml`.
"""

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from pydantic_settings_manager import clear_user_configs, load_user_configs

from kiarina.agi.chat_provider_impl.anthropic_vertex import (
    AnthropicVertexChatProvider,
    AnthropicVertexChatProviderSettings,
)
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.message import HumanMessage
from kiarina.agi.run_context import RunContext
from kiarina.utils.file import read_yaml_dict


def _create_provider(**kwargs: Any) -> AnthropicVertexChatProvider:
    provider = AnthropicVertexChatProvider(
        AnthropicVertexChatProviderSettings(**kwargs)
    )
    provider.name = "anthropic_vertex"
    return provider


class _Credentials:
    project_id = "from-credentials"


def test_create_client(monkeypatch: pytest.MonkeyPatch) -> None:
    import kiarina.lib.google

    monkeypatch.setattr(
        kiarina.lib.google,
        "get_cloud_options",
        lambda **kwargs: {"credentials": _Credentials()},
    )
    provider = _create_provider(vertex_ai_location="us-east5")

    client: Any = provider.client

    assert client.project_id == "from-credentials"
    assert client.region == "us-east5"
    assert provider.token_count_model_name == "claude-haiku-4-5@20251001"


def test_resolve_project_id(monkeypatch: pytest.MonkeyPatch) -> None:
    import google.auth

    provider = _create_provider()

    monkeypatch.setattr(google.auth, "default", lambda: (None, "from-default"))
    assert provider._resolve_project_id(None) == "from-default"

    def fail() -> None:
        raise RuntimeError("no credentials")

    monkeypatch.setattr(google.auth, "default", fail)
    assert provider._resolve_project_id(None) is None


def test_resolve_project_id_from_settings() -> None:
    user_configs: dict[str, Any] = {
        "kiarina.lib.google": {"configs": {"default": {"project_id": "from-settings"}}}
    }
    load_user_configs(user_configs)

    try:
        assert _create_provider()._resolve_project_id(None) == "from-settings"
    finally:
        clear_user_configs(user_configs)


# --------------------------------------------------
# Use Cases (Vertex AI)
# --------------------------------------------------


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


@pytest.mark.costly
@pytest.mark.parametrize("streaming", [False, True])
async def test_hello(
    setup_settings: None,
    streaming: bool,
    cost_recorder: CostRecorder,
    run_context: RunContext,
) -> None:
    provider = _create_provider(max_output_tokens=200)

    ai_messages = [
        ai_message
        async for ai_message in provider.run(
            [HumanMessage.create("Hello")],
            streaming=streaming,
            cost_recorder=cost_recorder,
            run_context=run_context,
        )
    ]

    print(ai_messages[-1].to_text())

    assert ai_messages[-1].to_text()


# --------------------------------------------------
# Use Cases (Anthropic API through a Vertex AI relay)
# --------------------------------------------------


class _VertexToAnthropicRelay:
    """
    Forwards the SDK's Vertex AI requests to the Anthropic API, so the Vertex
    request path can be checked without Vertex AI quota.
    """

    def __init__(self, api_key: str) -> None:
        import httpx2

        self.api_key = api_key
        self.upstream = httpx2.AsyncClient(timeout=120)
        self.methods: set[str] = set()

    async def handle_async_request(self, request: Any) -> Any:
        import json
        import re

        import httpx2

        body = json.loads(request.content)
        assert body.pop("anthropic_version") == "vertex-2023-10-16"

        match = re.search(
            r"/models/([^/:]+):(rawPredict|streamRawPredict)$", request.url.path
        )
        assert match, request.url.path
        model, method = match.groups()
        self.methods.add(f"{model}:{method}")

        if model == "count-tokens":
            assert body["model"] == "claude-haiku-4-5@20251001"
            url = "https://api.anthropic.com/v1/messages/count_tokens"
        else:
            assert model == "claude-haiku-4-5@20251001"
            url = "https://api.anthropic.com/v1/messages"

        body["model"] = "claude-haiku-4-5-20251001"
        upstream = await self.upstream.send(
            self.upstream.build_request(
                "POST",
                url,
                json=body,
                headers={"x-api-key": self.api_key, "anthropic-version": "2023-06-01"},
            ),
            stream=True,
        )
        return httpx2.Response(
            upstream.status_code,
            headers=upstream.headers,
            stream=upstream.stream,
            request=request,
        )


@pytest.mark.costly
async def test_relay_to_anthropic_api(
    load_settings: None,
    cost_recorder: CostRecorder,
    run_context: RunContext,
) -> None:
    import httpx2
    from anthropic import AsyncAnthropicVertex

    import kiarina.lib.anthropic
    from kiarina.agi.chat_provider import TokenOverflowError

    api_key = kiarina.lib.anthropic.settings_manager.get_settings().api_key
    assert api_key is not None

    relay = _VertexToAnthropicRelay(api_key.get_secret_value())
    provider = _create_provider(max_output_tokens=200)
    provider._client = AsyncAnthropicVertex(
        region="us-east5",
        project_id="relay",
        access_token="relay",
        http_client=httpx2.AsyncClient(transport=relay),  # type: ignore[arg-type]
        max_retries=0,
    )

    for streaming in (False, True):
        ai_messages = [
            ai_message
            async for ai_message in provider.run(
                [HumanMessage.create("Hello")],
                streaming=streaming,
                cost_recorder=cost_recorder,
                run_context=run_context,
            )
        ]
        assert ai_messages[-1].to_text()

    provider.settings.token_count_limit = 1

    with pytest.raises(TokenOverflowError):
        async for _ in provider.run(
            [HumanMessage.create("Hello")],
            cost_recorder=cost_recorder,
            run_context=run_context,
        ):
            pass

    assert relay.methods == {
        "claude-haiku-4-5@20251001:rawPredict",
        "claude-haiku-4-5@20251001:streamRawPredict",
        "count-tokens:rawPredict",
    }
