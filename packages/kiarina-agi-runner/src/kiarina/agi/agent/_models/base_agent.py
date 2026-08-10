import os
from collections.abc import AsyncIterator
from contextlib import suppress
from typing import Any

from kiarina.agi.asset_repository import create_asset_repository
from kiarina.agi.event import Event, dehydrate_events
from kiarina.agi.file import URIOrFilePath, get_file_blob
from kiarina.agi.file_info import FileInfo, deduplicate_file_infos
from kiarina.agi.file_info_adjuster import adjust_files
from kiarina.agi.file_info_builder import rebuild_file_info
from kiarina.agi.file_segment_normalizer import normalize_file_segments
from kiarina.agi.history import History
from kiarina.agi.message import ToolCall
from kiarina.agi.run_context import get_node_id
from kiarina.agi.tool import ToolNotFoundError, run_tool
from kiarina.agi.tool_info import ToolName
from kiarina.agi.workflow import run_workflow
from kiarina.utils.file import FileBlob
from kiarina.utils.file.asyncio import read_file

from .._exceptions.missing_tools_error import MissingToolsError
from .._schemas.agent_context import AgentContext
from .._types.agent import Agent
from .._types.agent_name import AgentName


class BaseAgent(Agent):
    def __init__(self, **kwargs: Any) -> None:
        self.init_kwargs: dict[str, Any] = kwargs
        self._name: AgentName | None = None

    @property
    def name(self) -> AgentName:
        if not self._name:  # pragma: no cover
            raise AssertionError("Agent name not set")

        return self._name

    @name.setter
    def name(self, value: AgentName) -> None:
        self._name = value

    def __str__(self) -> str:
        return self.__class__.__name__

    async def pre_run(
        self, ctx: AgentContext, history: History
    ) -> AsyncIterator[Event]:
        async for event in self._pre_run(ctx, history):
            yield event

        history.events, history.file_infos = dehydrate_events(
            history.events, history.file_infos
        )

        history.file_infos = deduplicate_file_infos(history.file_infos)
        history.file_infos = await self._update_file_infos(ctx, history)
        history.file_infos = await self._prepare_file_infos(ctx, history.file_infos)

    async def run(self, ctx: AgentContext, history: History) -> AsyncIterator[Event]:
        messages = history.get_messages()

        if not messages:
            raise ValueError("No message found in history")

        last_message = messages[-1]

        if last_message.type == "ai" and not last_message.tool_calls:
            raise ValueError("Last AI message has no tool calls")

        if tool_calls := history.get_pending_tool_calls():
            missing_tool_names: list[ToolName] = []

            for tool_call in tool_calls:
                try:
                    async for event in self._run_tool(ctx, history, tool_call):
                        if not event.transient:
                            history.add_event(event)

                        yield event

                except ToolNotFoundError as e:
                    missing_tool_names.append(e.tool_name)

            if missing_tool_names:
                raise MissingToolsError(missing_tool_names)

        else:
            async for event in self._run_workflow(ctx, history):
                if not event.transient:
                    history.add_event(event)

                yield event

    async def post_run(
        self, ctx: AgentContext, history: History
    ) -> AsyncIterator[Event]:
        if False:  # pragma: no cover
            yield

    # --------------------------------------------------
    # Template Methods (pre_run)
    # --------------------------------------------------

    async def _pre_run(
        self, ctx: AgentContext, history: History
    ) -> AsyncIterator[Event]:
        if False:  # pragma: no cover
            yield

    async def _update_file_infos(
        self, ctx: AgentContext, history: History
    ) -> list[FileInfo]:
        node_id = get_node_id()

        new_file_infos = [fi for fi in history.file_infos if fi.node_id != node_id]

        file_infos = [fi for fi in history.file_infos if fi.node_id == node_id]

        file_blobs: dict[URIOrFilePath, FileBlob] = {}

        for file_info in file_infos:
            if file_info.uri_or_file_path in file_blobs:
                continue

            with suppress(IsADirectoryError):
                if file_blob := await get_file_blob(
                    file_info.uri_or_file_path, run_context=ctx.run_context
                ):
                    file_blobs[file_info.uri_or_file_path] = file_blob

        file_infos = [fi for fi in file_infos if fi.uri_or_file_path in file_blobs]

        async def reload(file_info: FileInfo) -> FileInfo:
            file_blob = file_blobs[file_info.uri_or_file_path]

            if file_info.file_hash == file_blob.hash_string:
                return file_info

            return (
                await rebuild_file_info(
                    file_info,
                    file_blob,
                    run_context=ctx.run_context,
                )
            ).file_info

        file_infos = [await reload(fi) for fi in file_infos]

        file_infos = await normalize_file_segments(
            file_infos,
            file_blobs,
            run_context=ctx.run_context,
        )

        file_infos = await adjust_files(
            file_infos,
            file_blobs,
            ctx.file_limits,
            run_context=ctx.run_context,
        )

        new_file_infos.extend(file_infos)
        new_file_infos.sort(key=lambda fi: fi.created_at)

        return new_file_infos

    async def _prepare_file_infos(
        self, ctx: AgentContext, file_infos: list[FileInfo]
    ) -> list[FileInfo]:
        asset_repository = create_asset_repository(ctx.run_context)

        new_file_infos: list[FileInfo] = []
        changed = False

        for file_info in file_infos:
            if file_info.prepared:
                new_file_infos.append(file_info)
                continue

            file_blob = (
                await read_file(file_info.intermediate_file_path)
                if file_info.intermediate_file_path
                else await get_file_blob(
                    file_info.uri_or_file_path, run_context=ctx.run_context
                )
            )

            if not file_blob:
                changed = True
                continue

            asset_uri = asset_repository.generate_cache_uri(
                os.path.join("files", file_blob.hashed_file_name),
            )

            await asset_repository.set(
                asset_uri,
                file_blob.mime_type,
                file_blob.raw_data,
                only_not_exists=True,
            )

            new_file_info = file_info.model_copy(update={"asset_uri": asset_uri})
            new_file_infos.append(new_file_info)
            changed = True

        return new_file_infos if changed else file_infos

    # --------------------------------------------------
    # Template Methods (run)
    # --------------------------------------------------

    async def _run_workflow(
        self,
        ctx: AgentContext,
        history: History,
    ) -> AsyncIterator[Event]:
        async for event in run_workflow(
            history,
            **ctx.to_workflow_kwargs(),
            run_context=ctx.run_context,
        ):
            yield event

    async def _run_tool(
        self,
        ctx: AgentContext,
        history: History,
        tool_call: ToolCall,
    ) -> AsyncIterator[Event]:
        async for event in run_tool(
            tool_call,
            history=history,
            **ctx.to_tool_kwargs(),
            run_context=ctx.run_context,
        ):
            yield event
