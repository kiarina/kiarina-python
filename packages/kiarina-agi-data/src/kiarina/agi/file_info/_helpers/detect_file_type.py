from kiarina.utils.file import FileBlob

from .._types.file_type import FileType


def detect_file_type(file_blob: FileBlob) -> FileType:
    if file_blob.mime_type == "application/pdf":
        return "pdf"
    elif file_blob.mime_type.startswith("image/"):
        return "image"
    elif file_blob.mime_type.startswith("audio/"):
        return "audio"
    elif file_blob.mime_type.startswith("video/"):
        return "video"
    elif file_blob.is_text():
        return "text"
    else:
        return "other"
