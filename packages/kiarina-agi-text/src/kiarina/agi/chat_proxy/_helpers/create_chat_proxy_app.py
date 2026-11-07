import asyncio
import contextlib
import logging
import secrets
from collections.abc import AsyncIterator
from typing import Annotated

from kiarina.agi.chat_model import ChatModel, chat_model_registry
from kiarina.agi.cost_recorder_impl.null import NullCostRecorder
from kiarina.agi.message import Message
from kiarina.utils.app import user_directory

from .._exceptions.chat_proxy_error import ChatProxyError
from .._exceptions.chat_proxy_missing_files_error import ChatProxyMissingFilesError
from .._operations.attach_chat_proxy_files import attach_chat_proxy_files
from .._operations.expire_chat_proxy_cache import expire_chat_proxy_cache
from .._operations.find_missing_chat_proxy_files import find_missing_chat_proxy_files
from .._schemas.chat_proxy_error_info import ChatProxyErrorInfo
from .._schemas.chat_proxy_event import ChatProxyEvent
from .._schemas.chat_proxy_missing_files import ChatProxyMissingFiles
from .._schemas.chat_proxy_missing_files_request import ChatProxyMissingFilesRequest
from .._schemas.chat_proxy_model_info import ChatProxyModelInfo
from .._schemas.chat_proxy_request import ChatProxyRequest
from .._settings import ChatProxySettings, settings_manager

try:
    from fastapi import Depends, FastAPI, Header, HTTPException
    from fastapi.responses import JSONResponse, Response, StreamingResponse
except ImportError as exc:
    raise ImportError(
        "fastapi is required to use the chat proxy. "
        "Install it with: pip install 'kiarina-agi-text[chat-proxy]'"
    ) from exc

logger = logging.getLogger(__name__)

_EXPIRE_INTERVAL_SECONDS = 3600


def create_chat_proxy_app(settings: ChatProxySettings | None = None) -> FastAPI:
    if settings is None:
        settings = settings_manager.get_settings()

    semaphore = asyncio.Semaphore(settings.max_concurrency)

    @contextlib.asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        task = (
            asyncio.create_task(_expire_cache(settings.cache_ttl))
            if settings.cache_ttl > 0
            else None
        )

        try:
            yield
        finally:
            if task is not None:
                task.cancel()

                with contextlib.suppress(asyncio.CancelledError):
                    await task

    app = FastAPI(title="kiarina chat proxy", lifespan=lifespan)

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

    @app.post("/v1/files/missing", dependencies=[Depends(authorize)])
    async def find_missing_files(
        request: ChatProxyMissingFilesRequest,
    ) -> ChatProxyMissingFiles:
        return ChatProxyMissingFiles(
            missing=await find_missing_chat_proxy_files(
                request.sha256s, run_context=request.run_context
            )
        )

    @app.post("/v1/chat", dependencies=[Depends(authorize)])
    async def chat(request: ChatProxyRequest) -> Response:
        chat_model = resolve_chat_model(request.model_name)

        try:
            messages = await attach_chat_proxy_files(
                request.messages, request.files, run_context=request.run_context
            )
        except ChatProxyMissingFilesError as e:
            return JSONResponse(status_code=409, content={"missing": e.hashes})
        except ChatProxyError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

        return StreamingResponse(
            _run_chat(chat_model, messages, request, semaphore),
            media_type="application/x-ndjson",
        )

    return app


async def _expire_cache(ttl: int) -> None:
    cache_dir = str(user_directory.get_user_cache_dir())

    while True:
        try:
            deleted = await asyncio.to_thread(expire_chat_proxy_cache, cache_dir, ttl)

            if deleted:
                logger.info(f"Deleted {deleted} expired files from {cache_dir}")

        except Exception:
            logger.exception(f"Failed to expire files in {cache_dir}")

        await asyncio.sleep(min(ttl, _EXPIRE_INTERVAL_SECONDS))


async def _run_chat(
    chat_model: ChatModel,
    messages: list[Message],
    request: ChatProxyRequest,
    semaphore: asyncio.Semaphore,
) -> AsyncIterator[str]:
    async with semaphore:
        cost_recorder = NullCostRecorder()
        error: ChatProxyErrorInfo | None = None

        try:
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
