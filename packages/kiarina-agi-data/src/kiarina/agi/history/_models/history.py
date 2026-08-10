from typing import Any

from pydantic import BaseModel, Field

from kiarina.agi.embedding import (
    Embedding,
    EmbeddingID,
    EmbeddingKind,
    EmbeddingSpaceID,
)
from kiarina.agi.event import (
    Event,
    EventType,
    dehydrate_event,
    message_to_event,
)
from kiarina.agi.file import URIOrFilePath
from kiarina.agi.file_info import FileID, FileInfo, Group, UniqueKey
from kiarina.agi.file_info_pool import FileInfoPool
from kiarina.agi.message import Message, MessageType, ToolCall
from kiarina.agi.tool_info import ToolInfo, ToolName, ToolState


class History(BaseModel):
    events: list[Event] = Field(default_factory=list)
    file_infos: FileInfoPool = Field(default_factory=list)
    tool_infos: list[ToolInfo] = Field(default_factory=list)
    embeddings: dict[EmbeddingID, Embedding] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def clear(self) -> None:
        self.events.clear()
        self.file_infos.clear()
        self.tool_infos.clear()
        self.embeddings.clear()
        self.metadata.clear()

    # --------------------------------------------------
    # Event Management
    # --------------------------------------------------

    def get_last_event(self, event_type: EventType) -> Event | None:
        for event in reversed(self.events):
            if event.type == event_type:
                return event

        return None

    def get_pending_tool_calls(self) -> list[ToolCall]:
        pendings: list[ToolCall] = []
        completed_ids: set[str] = set()

        for message in reversed(self.get_messages()):
            if message.type == "tool":
                completed_ids.add(message.tool_call_id)
                continue

            if message.type != "ai" or not message.tool_calls:
                break

            for tool_call in message.tool_calls:
                if tool_call.id not in completed_ids:
                    pendings.append(tool_call)

            break

        return pendings

    def add_event(self, event: Event) -> None:
        event, self.file_infos = dehydrate_event(event, self.file_infos)
        self.events.append(event)

    def replace_event(self, target: Event, replacement: Event) -> None:
        replacement, self.file_infos = dehydrate_event(replacement, self.file_infos)

        for i, event in enumerate(self.events):
            if event is target:
                self.events[i] = replacement
                return

        raise ValueError("Target event not found in history")

    # --------------------------------------------------
    # Message Management
    # --------------------------------------------------

    def get_last_message(self, message_type: MessageType) -> Message | None:
        for event in reversed(self.events):
            if (
                event.type == "ai_message"
                or event.type == "human_message"
                or event.type == "tool_message"
            ):
                if event.message.type == message_type:
                    return event.message

        return None

    def get_messages(self) -> list[Message]:
        return [
            e.message
            for e in self.events
            if (
                e.type == "ai_message"
                or e.type == "human_message"
                or e.type == "tool_message"
            )
        ]

    def add_message(self, message: Message) -> None:
        self.add_event(message_to_event(message))

    # --------------------------------------------------
    # File Info Management
    # --------------------------------------------------

    def get_file_info(
        self,
        *,
        unique_key: UniqueKey,
    ) -> FileInfo | None:
        for fi in self.file_infos:
            if fi.unique_key == unique_key:
                return fi

        return None

    def get_file_infos(
        self,
        *,
        uri_or_file_path: URIOrFilePath | None = None,
        group: Group | None = None,
        no_group: bool = False,
        no_unique_key: bool = False,
        ignore_unique_keys: list[UniqueKey] | None = None,
        in_message: bool | None = None,
    ) -> list[FileInfo]:
        file_infos = self.file_infos.copy()

        if uri_or_file_path is not None:
            file_infos = [
                fi for fi in file_infos if fi.uri_or_file_path == uri_or_file_path
            ]

        if group is not None:
            file_infos = [fi for fi in file_infos if fi.group == group]

        if no_group:
            file_infos = [fi for fi in file_infos if fi.group is None]

        if no_unique_key:
            file_infos = [fi for fi in file_infos if fi.unique_key is None]

        if ignore_unique_keys:
            file_infos = [
                fi for fi in file_infos if fi.unique_key not in ignore_unique_keys
            ]

        if in_message is not None:
            message_file_ids = {
                fi.id
                for message in self.get_messages()
                for fi in message.get_file_infos()
            }

            if in_message:
                file_infos = [fi for fi in file_infos if fi.id in message_file_ids]
            else:
                file_infos = [fi for fi in file_infos if fi.id not in message_file_ids]

        return file_infos

    def add_file_info(self, file_info: FileInfo) -> None:
        self.file_infos.append(file_info)

    def remove_file_info(self, file_id: FileID) -> None:
        self.file_infos = [fi for fi in self.file_infos if fi.id != file_id]

    # --------------------------------------------------
    # Tool Info Management
    # --------------------------------------------------

    def get_tool_info(self, name: ToolName) -> ToolInfo | None:
        for tool_info in self.tool_infos:
            if tool_info.name == name:
                return tool_info

        return None

    def get_tool_infos(
        self,
        *,
        state: ToolState | None = None,
    ) -> list[ToolInfo]:
        tool_infos = self.tool_infos.copy()

        if state is not None:
            tool_infos = [
                tool_info for tool_info in tool_infos if tool_info.state == state
            ]

        return tool_infos

    def add_tool_info(self, tool_info: ToolInfo) -> None:
        self.remove_tool_info(tool_info.name)
        self.tool_infos.append(tool_info)

    def remove_tool_info(self, name: ToolName) -> None:
        self.tool_infos = [
            tool_info for tool_info in self.tool_infos if tool_info.name != name
        ]

    # --------------------------------------------------
    # Embedding Management
    # --------------------------------------------------

    def get_embedding(self, embedding_id: EmbeddingID) -> Embedding | None:
        return self.embeddings.get(embedding_id)

    def add_embedding(self, embedding: Embedding) -> None:
        self.embeddings[embedding.id] = embedding

    def remove_embedding(self, embedding_id: EmbeddingID) -> None:
        if embedding_id in self.embeddings:
            del self.embeddings[embedding_id]

    def get_embeddings(
        self,
        *,
        kind: EmbeddingKind | None = None,
        space_id: EmbeddingSpaceID | None = None,
    ) -> list[Embedding]:
        embeddings = list(self.embeddings.values())

        if kind is not None:
            embeddings = [e for e in embeddings if e.kind == kind]

        if space_id is not None:
            embeddings = [e for e in embeddings if e.space_id == space_id]

        return embeddings
