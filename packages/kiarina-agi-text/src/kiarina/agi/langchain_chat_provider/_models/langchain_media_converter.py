from typing import Any

from kiarina.utils.mime import MIMEBlob


class LangChainMediaConverter:
    def to_image_content(self, mime_blob: MIMEBlob) -> dict[str, Any] | None:
        return None

    def to_audio_content(self, mime_blob: MIMEBlob) -> dict[str, Any] | None:
        return None

    def to_video_content(self, mime_blob: MIMEBlob) -> dict[str, Any] | None:
        return None

    def to_pdf_content(
        self, mime_blob: MIMEBlob, *, display_name: str
    ) -> dict[str, Any] | None:
        return None
