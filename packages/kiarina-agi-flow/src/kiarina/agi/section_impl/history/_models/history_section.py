from collections.abc import AsyncIterator

from kiarina.agi.event import Event
from kiarina.agi.file_info import shrink_file_infos
from kiarina.agi.file_info_pool import FileInfoPool
from kiarina.agi.message import Message, hydrate_messages
from kiarina.agi.section import BaseSection
from kiarina.agi.token_utils import TokenCount


class HistorySection(BaseSection):
    def __init__(
        self,
        *,
        min_message_count: int = 1,
        reserve_per_file: TokenCount = 20000,
    ) -> None:
        super().__init__()

        self.min_message_count: int = min_message_count
        self.reserve_per_file: TokenCount = reserve_per_file

        self.messages: list[Message] = []
        self.pool: FileInfoPool = []

    async def prepare(self) -> AsyncIterator[Event]:
        self.messages = self.ctx.history.get_messages()
        self.pool = self.ctx.history.get_file_infos(in_message=True)

        if False:  # pragma: no cover
            yield

    def get_messages(self) -> list[Message]:
        messages = self.messages.copy()

        if self.pool:
            messages = self._hydrate_messages(messages, self.pool)

        return self._populate_cache_control(messages)

    def is_resizable(self) -> bool:
        if len(self.pool) > 0:
            return True

        messages = self._resize_messages(self.messages)

        if len(messages) >= self.min_message_count:
            return True

        return False

    async def resize(self, reduce: TokenCount) -> AsyncIterator[Event]:
        reduced = 0

        if self.messages:
            reduced += self._resize_last_message(reduce)

        if reduced < reduce:
            if len(self.pool) > 0:
                reduced += self._shrink_pool(reduce - reduced)

        if reduced < reduce:
            messages = self._resize_messages(self.messages)

            if len(messages) >= self.min_message_count:
                self.messages = messages

        if False:  # pragma: no cover
            yield

    # --------------------------------------------------
    # Private Methods (Message Generation)
    # --------------------------------------------------

    def _hydrate_messages(
        self,
        messages: list[Message],
        pool: FileInfoPool,
    ) -> list[Message]:
        messages.reverse()
        messages, _ = hydrate_messages(messages, pool)
        messages.reverse()
        return messages

    def _populate_cache_control(self, messages: list[Message]) -> list[Message]:
        last_message: Message | None = None

        for message in reversed(messages):
            if message.type == "human" or message.type == "tool":
                last_message = message
                break

        if last_message is None:  # pragma: no cover
            return messages

        last_content = last_message.contents[-1] if last_message.contents else None

        if (
            not last_content or last_content.cache_control is not None
        ):  # pragma: no cover
            return messages

        new_last_content = last_content.model_copy(
            update={"cache_control": {"type": "ephemeral"}}
        )

        new_last_message = last_message.replace_content(last_content, new_last_content)

        return [
            new_last_message if message is last_message else message
            for message in messages
        ]

    # --------------------------------------------------
    # Private Methods (Resizing)
    # --------------------------------------------------

    def _resize_last_message(self, reduce: TokenCount) -> TokenCount:
        assert len(self.messages) > 0

        self.pool, reduced = self.messages[-1].shrink(
            self.pool,
            reduce,
            reserve=self.reserve_per_file,
        )

        return reduced

    def _shrink_pool(self, reduce: TokenCount) -> TokenCount:
        self.pool.sort(key=lambda fi: fi.created_at)
        self.pool, reduced = shrink_file_infos(self.pool, reduce=reduce)
        self.pool = [fi for fi in self.pool if not fi.metadata_only]
        return reduced

    def _resize_messages(self, messages: list[Message]) -> list[Message]:
        if not messages:
            return []

        if messages[0].type == "human":
            # Anthropic does not allow AIMessage without HumanMessage
            offset = 1

            for message in messages[1:]:
                if message.type == "human":
                    break
                else:
                    offset += 1

            return messages[offset:]

        elif messages[0].type == "ai":
            if not messages[0].tool_calls:
                return messages[1:]

            offset = 1

            for message in messages[1:]:
                if message.type == "tool":
                    offset += 1
                else:
                    break

            return messages[offset:]

        elif messages[0].type == "tool":  # pragma: no cover
            offset = 1

            for message in messages[1:]:
                if message.type == "tool":
                    offset += 1
                else:
                    break

            return messages[offset:]

        else:  # pragma: no cover
            raise AssertionError(f"Unexpected message type: {messages[0].type}")
