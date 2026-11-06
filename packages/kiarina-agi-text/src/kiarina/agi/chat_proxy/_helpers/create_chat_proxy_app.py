import asyncio
import secrets
from collections.abc import AsyncIterator
from typing import Annotated

from kiarina.agi.chat_model import ChatModel, chat_model_registry
from kiarina.agi.cost_recorder_impl.null import NullCostRecorder

from .._operations.attach_chat_proxy_files import attach_chat_proxy_files
from .._schemas.chat_proxy_error_info import ChatProxyErrorInfo
from .._schemas.chat_proxy_event import ChatProxyEvent
from .._schemas.chat_proxy_model_info import ChatProxyModelInfo
from .._schemas.chat_proxy_request import ChatProxyRequest
from .._settings import ChatProxySettings, settings_manager

try:
    from fastapi import Depends, FastAPI, Header, HTTPException
    from fastapi.responses import StreamingResponse
except ImportError as exc:
    raise ImportError(
        "fastapi is required to use the chat proxy. "
        "Install it with: pip install 'kiarina-agi-text[chat-proxy]'"
    ) from exc


def create_chat_proxy_app(settings: ChatProxySettings | None = None) -> FastAPI:
    if settings is None:
        settings = settings_manager.get_settings()

    semaphore = asyncio.Semaphore(settings.max_concurrency)
    app = FastAPI(title="kiarina chat proxy")

    def authorize(
        authorization: Annotated[str | None, Header()] = None,
    ) -> None:
        if settings.token is None:
            return

        expected = f"Bearer {settings.token.get_secret_value()}"

        if not authorization or not secrets.compare_digest(authorization, expected):
            raise HTTPException(status_code=401, detail="Invalid token")

    def resolve_chat_model(model_name: str) -> ChatModel:
        if (
            settings.allowed_models is not None
            and model_name not in settings.allowed_models
        ):
            raise HTTPException(status_code=403, detail=f"Not allowed: {model_name}")

        try:
            chat_model = chat_model_registry.get(model_name)
        except (KeyError, ValueError) as e:
            raise HTTPException(status_code=404, detail=str(e)) from e

        if chat_model.provider_name == "proxy":
            raise HTTPException(
                status_code=400, detail=f"{model_name} is itself a proxy chat model"
            )

        return chat_model

    @app.get("/v1/chat-models/{model_name}", dependencies=[Depends(authorize)])
    def get_chat_model(model_name: str) -> ChatProxyModelInfo:
        chat_model = resolve_chat_model(model_name)

        return ChatProxyModelInfo(
            name=chat_model.name, capabilities=chat_model.get_capabilities()
        )

    @app.post("/v1/chat", dependencies=[Depends(authorize)])
    async def chat(request: ChatProxyRequest) -> StreamingResponse:
        chat_model = resolve_chat_model(request.model_name)

        return StreamingResponse(
            _run_chat(chat_model, request, semaphore),
            media_type="application/x-ndjson",
        )

    return app


async def _run_chat(
    chat_model: ChatModel,
    request: ChatProxyRequest,
    semaphore: asyncio.Semaphore,
) -> AsyncIterator[str]:
    async with semaphore:
        cost_recorder = NullCostRecorder()
        error: ChatProxyErrorInfo | None = None

        try:
            messages = await attach_chat_proxy_files(
                request.messages, request.files, run_context=request.run_context
            )

            async for message in chat_model.run(
                messages,
                tool_infos=request.tool_infos,
                tool_choice=request.tool_choice,
                parallel_tool_calls=request.parallel_tool_calls,
                streaming=request.streaming,
                cost_recorder=cost_recorder,
                run_context=request.run_context,
            ):
                if message.type == "ai_chunk":
                    yield _to_line(ChatProxyEvent(type="chunk", message=message))
                else:
                    yield _to_line(ChatProxyEvent(type="message", message=message))

        except Exception as e:
            error = ChatProxyErrorInfo.from_exception(e)

        for cost_record in cost_recorder.records:
            yield _to_line(ChatProxyEvent(type="cost", cost_record=cost_record))

        if error is not None:
            yield _to_line(ChatProxyEvent(type="error", error=error))


def _to_line(event: ChatProxyEvent) -> str:
    return event.model_dump_json() + "\n"
