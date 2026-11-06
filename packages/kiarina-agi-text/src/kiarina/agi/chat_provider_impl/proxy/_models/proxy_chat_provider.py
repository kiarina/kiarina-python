import json
from collections.abc import AsyncIterator

from kiarina.agi.chat_provider import (
    BaseChatProvider,
    ChatCapabilities,
    ChatProviderContext,
)
from kiarina.agi.chat_proxy import (
    ChatProxyError,
    ChatProxyEvent,
    ChatProxyModelInfo,
    ChatProxyRequest,
    collect_chat_proxy_files,
)
from kiarina.agi.message import AIMessage, AIMessageChunk

from .._settings import ProxyChatProviderSettings

try:
    import httpx
except ImportError as exc:
    raise ImportError(
        "httpx is required to use ProxyChatProvider. "
        "Install it with: pip install 'kiarina-agi-text[chat-provider-proxy]'"
    ) from exc


class ProxyChatProvider(BaseChatProvider):
    def __init__(
        self,
        settings: ProxyChatProviderSettings,
        *,
        client: httpx.Client | None = None,
        async_client: httpx.AsyncClient | None = None,
    ) -> None:
        super().__init__()

        self.settings: ProxyChatProviderSettings = settings
        self._client: httpx.Client | None = client
        self._async_client: httpx.AsyncClient | None = async_client
        self._capabilities: ChatCapabilities | None = None
        self._known_hashes: set[str] = set()

    def get_capabilities(self) -> ChatCapabilities:
        if self._capabilities is None:
            path = f"/v1/chat-models/{self.settings.model_name}"

            if self._client is not None:
                response = self._client.get(path, headers=self._headers())
            else:
                with httpx.Client(
                    base_url=self.settings.base_url, timeout=self.settings.timeout
                ) as client:
                    response = client.get(path, headers=self._headers())

            _raise_for_status(response.status_code, response.text)
            info = ChatProxyModelInfo.model_validate_json(response.content)
            self._capabilities = info.capabilities

        return self._capabilities

    async def _run(
        self, ctx: ChatProviderContext
    ) -> AsyncIterator[AIMessageChunk | AIMessage]:
        if self._async_client is not None:
            async for message in self._stream(self._async_client, ctx):
                yield message
            return

        async with httpx.AsyncClient(
            base_url=self.settings.base_url, timeout=self.settings.timeout
        ) as client:
            async for message in self._stream(client, ctx):
                yield message

    async def _stream(
        self, client: httpx.AsyncClient, ctx: ChatProviderContext
    ) -> AsyncIterator[AIMessageChunk | AIMessage]:
        # The first try leaves out the files the proxy took before. If it lost
        # them, it answers 409 with their hashes, and the second try sends them.
        for attempt in range(2):
            files = await collect_chat_proxy_files(
                ctx.messages,
                run_context=ctx.run_context,
                known_hashes=self._known_hashes,
            )
            request = ChatProxyRequest(
                model_name=self.settings.model_name,
                messages=ctx.messages,
                tool_infos=ctx.tool_infos,
                tool_choice=ctx.tool_choice,
                parallel_tool_calls=ctx.parallel_tool_calls,
                streaming=ctx.streaming,
                run_context=ctx.run_context,
                files=files,
            )

            async with client.stream(
                "POST",
                "/v1/chat",
                content=request.model_dump_json(),
                headers={**self._headers(), "Content-Type": "application/json"},
            ) as response:
                if response.status_code == 409 and attempt == 0:
                    missing = json.loads(await response.aread()).get("missing", [])
                    self._known_hashes.difference_update(missing)
                    continue

                if response.status_code != 200:
                    text = (await response.aread()).decode(errors="replace")
                    _raise_for_status(response.status_code, text)

                self._known_hashes.update(file.sha256 for file in files.values())

                async for message in _read_events(response, ctx):
                    yield message

                return

    def _headers(self) -> dict[str, str]:
        if self.settings.token is None:
            return {}

        return {"Authorization": f"Bearer {self.settings.token.get_secret_value()}"}


async def _read_events(
    response: httpx.Response, ctx: ChatProviderContext
) -> AsyncIterator[AIMessageChunk | AIMessage]:
    final: AIMessage | None = None

    async for line in response.aiter_lines():
        if not line.strip():
            continue

        event = ChatProxyEvent.model_validate_json(line)

        if event.type == "chunk" and event.message is not None:
            yield event.message
        elif event.type == "message" and event.message is not None:
            final = event.message
            yield final
        elif event.type == "cost" and event.cost_record is not None:
            ctx.cost_recorder.add(event.cost_record)
        elif event.type == "error" and event.error is not None:
            raise event.error.to_exception()

    if final is None:
        raise ChatProxyError("The chat proxy ended without a message")


def _raise_for_status(status_code: int, body: str) -> None:
    if status_code != 200:
        raise ChatProxyError(f"The chat proxy returned {status_code}: {body}")
