from kiarina.agi.file_info import FileInfo

MEDIA_FILE_TYPES = ("image", "audio", "video", "pdf")


def get_file_key(file_info: FileInfo) -> str | None:
    """The key of a file whose contents the chat proxy needs, or None if it needs none."""
    if file_info.metadata_only or file_info.type not in MEDIA_FILE_TYPES:
        return None

    return file_info.asset_uri or file_info.uri_or_file_path
