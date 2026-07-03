from typing import Self

from pydantic import BaseModel, ValidationError

from kiarina.utils.common import parse_config_string

from .._types.chat_limits_specifier import ChatLimitsSpecifier


class ChatLimits(BaseModel):
    token_count_limit: int = 772_000
    """
    Token count limit per request
    """

    file_size_limit: int = 20_000_000  # 20 MB
    """
    Total file size limit per request (in bytes)

    Reference:
    - OpenAI: 50MB
    - Anthropic: 32MB
    - Google Gemini: 100MB
    """

    image_file_count_limit: int = 100
    """
    Image file count limit per request

    Reference:
    - OpenAI: 500 files
    - Anthropic: 100 files
    - Google Gemini: 3000 files
    """

    audio_duration_limit: float = 60 * 60 * 9.5
    """
    Audio duration limit per request (in seconds)

    Reference:
    - Google Gemini: 9.5 hours
    """

    audio_file_count_limit: int = 7
    """
    Audio file count limit per request

    Can be set freely as long as it is within other limits.
    """

    video_duration_limit: float = 60 * 60 * 1.0
    """
    Video duration limit per request (in seconds)

    Reference:
    - Google Gemini: 1 hour
    """

    video_file_count_limit: int = 7
    """
    Video file count limit per request

    Can be set freely as long as it is within other limits.
    """

    pdf_page_count_limit: int = 100
    """
    PDF page count limit per request

    Reference:
    - OpenAI: depends on tokens and file size
    - Anthropic: 100 pages
    - Google Gemini: 1000 pages
    """

    pdf_file_count_limit: int = 7
    """
    PDF file count limit per request

    Can be set freely as long as it is within other limits.
    """

    @property
    def token_count(self) -> str:
        return f"{self.token_count_limit} tokens"

    @property
    def file_size(self) -> str:
        return f"{self.file_size_limit} bytes"

    @property
    def image(self) -> str:
        return f"image({self.image_file_count_limit} files)"

    @property
    def audio(self) -> str:
        audio_props: list[str] = []
        audio_props.append(f"{self.audio_file_count_limit} files")
        audio_props.append(f"{self.audio_duration_limit} sec")
        return f"audio({','.join(audio_props)})"

    @property
    def video(self) -> str:
        video_props: list[str] = []
        video_props.append(f"{self.video_file_count_limit} files")
        video_props.append(f"{self.video_duration_limit} sec")
        return f"video({','.join(video_props)})"

    @property
    def pdf(self) -> str:
        pdf_props: list[str] = []
        pdf_props.append(f"{self.pdf_file_count_limit} files")
        pdf_props.append(f"{self.pdf_page_count_limit} pages")
        return f"pdf({','.join(pdf_props)})"

    def to_string(self) -> str:
        props: list[str] = []
        props.append(self.token_count)
        props.append(self.file_size)
        props.append(self.image)
        props.append(self.audio)
        props.append(self.video)
        props.append(self.pdf)
        return " ".join(props)

    def __str__(self) -> str:
        return self.to_string()

    @classmethod
    def from_specifier(cls, specifier: ChatLimitsSpecifier) -> Self:
        try:
            return cls.model_validate_json(specifier)

        except ValidationError:
            config = parse_config_string(
                specifier, separator="&", key_value_separator="="
            )
            return cls.model_validate(config)
