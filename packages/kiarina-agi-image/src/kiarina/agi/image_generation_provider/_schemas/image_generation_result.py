from dataclasses import dataclass

from kiarina.utils.mime import MIMEBlob


@dataclass
class ImageGenerationResult:
    mime_blob: MIMEBlob
