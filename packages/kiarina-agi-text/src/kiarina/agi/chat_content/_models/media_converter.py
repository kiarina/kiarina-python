from kiarina.utils.mime import MIMEBlob

from .._types.content_part import ContentPart


class MediaConverter:
    """
    Converts media into provider-specific content parts.

    Returning `None` leaves only the file's metadata in the message.
    """

    def to_image_content(self, mime_blob: MIMEBlob) -> ContentPart | None:
        return None

    def to_audio_content(self, mime_blob: MIMEBlob) -> ContentPart | None:
        return None

    def to_video_content(self, mime_blob: MIMEBlob) -> ContentPart | None:
        return None

    def to_pdf_content(
        self, mime_blob: MIMEBlob, *, display_name: str
    ) -> ContentPart | None:
        return None
