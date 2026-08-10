from pydantic import Field

from kiarina.agi.chat_limits import ChatLimits
from kiarina.agi.file_info import FileType
from kiarina.agi.message import MessageType


class ChatCapabilities(ChatLimits):
    input_enabled: dict[FileType, bool] = Field(default_factory=dict)
    output_enabled: dict[FileType, bool] = Field(default_factory=dict)

    def is_supported(self, file_type: FileType) -> bool:
        return self.can_include("human", file_type)

    def can_include(self, message_type: MessageType, file_type: FileType) -> bool:
        if file_type in ["text", "other"]:
            return True

        if message_type == "human":
            return self.input_enabled.get(file_type, False)
        elif message_type == "tool":
            return self.output_enabled.get(file_type, False)
        else:
            return False

    def to_string(self) -> str:
        props: list[str] = []
        props.append(self.token_count)
        props.append(self.file_size)

        if self.can_include("human", "image"):
            props.append(self.image)
        if self.can_include("tool", "image"):
            props.append("image_out")
        if self.can_include("human", "audio"):
            props.append(self.audio)
        if self.can_include("tool", "audio"):
            props.append("audio_out")
        if self.can_include("human", "video"):
            props.append(self.video)
        if self.can_include("tool", "video"):
            props.append("video_out")
        if self.can_include("human", "pdf"):
            props.append(self.pdf)
        if self.can_include("tool", "pdf"):
            props.append("pdf_out")

        return " ".join(props)
