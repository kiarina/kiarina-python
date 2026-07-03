from typing import Literal, Self

from pydantic import BaseModel


class ChatEstimates(BaseModel):
    token_count: int = 0
    file_size: int = 0

    text_file_count: int = 0
    text_token_count: int = 0

    image_file_count: int = 0
    image_token_count: int = 0

    audio_duration: float = 0.0
    audio_file_count: int = 0
    audio_token_count: int = 0

    video_duration: float = 0.0
    video_file_count: int = 0
    video_token_count: int = 0

    pdf_page_count: int = 0
    pdf_file_count: int = 0
    pdf_token_count: int = 0

    @property
    def summary(self) -> str:
        summary = f"{self.token_count} tokens"

        if self.file_size != 0:
            summary += f" {self.file_size} bytes"

        return summary

    @property
    def text(self) -> str:
        return f"text({self.text_token_count} tokens, {self.text_file_count} files)"

    @property
    def image(self) -> str:
        return f"image({self.image_token_count} tokens, {self.image_file_count} files)"

    @property
    def audio(self) -> str:
        return f"audio({self.audio_token_count} tokens, {self.audio_file_count} files, {self.audio_duration:.2f} sec)"

    @property
    def video(self) -> str:
        return f"video({self.video_token_count} tokens, {self.video_file_count} files, {self.video_duration:.2f} sec)"

    @property
    def pdf(self) -> str:
        return f"pdf({self.pdf_token_count} tokens, {self.pdf_file_count} files, {self.pdf_page_count} pages)"

    def add_token_count(
        self,
        target: Literal["text", "image", "audio", "video", "pdf"],
        token_count: int,
    ) -> None:
        if target == "text":
            self.text_token_count += token_count
        elif target == "image":
            self.image_token_count += token_count
        elif target == "audio":
            self.audio_token_count += token_count
        elif target == "video":
            self.video_token_count += token_count
        elif target == "pdf":
            self.pdf_token_count += token_count

        self.token_count += token_count

    def to_string(self) -> str:
        props: list[str] = [self.summary]

        if self.text_file_count != 0:
            props.append(self.text)
        if self.image_file_count != 0:
            props.append(self.image)
        if self.audio_file_count != 0:
            props.append(self.audio)
        if self.video_file_count != 0:
            props.append(self.video)
        if self.pdf_file_count != 0:
            props.append(self.pdf)

        return " ".join(props)

    def __str__(self) -> str:
        return self.to_string()

    def __add__(self, y: Self) -> Self:
        x = self.model_copy()

        x.token_count += y.token_count
        x.file_size += y.file_size

        x.text_file_count += y.text_file_count
        x.text_token_count += y.text_token_count

        x.image_file_count += y.image_file_count
        x.image_token_count += y.image_token_count

        x.audio_duration += y.audio_duration
        x.audio_file_count += y.audio_file_count
        x.audio_token_count += y.audio_token_count

        x.video_duration += y.video_duration
        x.video_file_count += y.video_file_count
        x.video_token_count += y.video_token_count

        x.pdf_page_count += y.pdf_page_count
        x.pdf_file_count += y.pdf_file_count
        x.pdf_token_count += y.pdf_token_count

        return x
