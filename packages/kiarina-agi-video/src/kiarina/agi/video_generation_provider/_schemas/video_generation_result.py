from dataclasses import dataclass

from kiarina.utils.mime import MIMEBlob


@dataclass
class VideoGenerationResult:
    video_mime_blob: MIMEBlob
    thumbnail_mime_blob: MIMEBlob | None = None
    spritesheet_mime_blob: MIMEBlob | None = None
