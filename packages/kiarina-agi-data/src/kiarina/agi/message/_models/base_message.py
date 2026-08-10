from typing import Self

from pydantic import BaseModel, Field

from kiarina.agi.chat_estimates import ChatEstimates
from kiarina.agi.content import Content
from kiarina.agi.file_info import FileInfo
from kiarina.agi.file_info_pool import FileInfoPool, find_file_index
from kiarina.agi.token_utils import TokenCount

from .._types.message_type import MessageType


class BaseMessage(BaseModel):
    type: MessageType = Field(frozen=True)
    contents: list[Content] = Field(default_factory=list)

    def get_file_infos(self) -> list[FileInfo]:
        return [file_info for content in self.contents for file_info in content.files]

    def contents_to_text(self) -> str:
        return "\n\n".join(
            [content.to_text() for content in self.contents if content.to_text()]
        )

    def to_estimates(self) -> ChatEstimates:
        estimates = ChatEstimates()

        if self.contents:
            estimates = sum(
                [content.to_estimates() for content in self.contents],
                estimates,
            )

        return estimates

    def to_text(self) -> str:
        return self.contents_to_text()

    def replace_content(self, old: Content, new: Content) -> Self:
        new_contents = [new if content is old else content for content in self.contents]

        if new_contents == self.contents:
            raise ValueError("Content not found in message")

        return self.model_copy(update={"contents": new_contents})

    def shrink(
        self, pool: FileInfoPool, reduce: TokenCount, reserve: TokenCount = 0
    ) -> tuple[FileInfoPool, TokenCount]:
        reduced = 0
        pool = pool.copy()

        file_infos = self.get_file_infos()
        file_infos.sort(key=lambda fi: fi.token_count, reverse=True)

        for file_info in file_infos:
            if not file_info.metadata_only:
                # Process only dehydrated file information
                continue

            index = find_file_index(pool, file_info.id)

            if index is None:
                # Skip if the file info is not found.
                continue

            new_file_info, new_reduced = pool[index].shrink(
                max(reduce - reduced, 0), reserve
            )

            if new_reduced > 0:
                reduced += new_reduced
                pool[index] = new_file_info

                if reduced >= reduce:
                    break

        return pool, reduced
