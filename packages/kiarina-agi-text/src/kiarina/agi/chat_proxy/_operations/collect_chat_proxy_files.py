import base64

from kiarina.agi.file import get_file_blob
from kiarina.agi.message import Message
from kiarina.agi.run_context import RunContext

from .._schemas.chat_proxy_file import ChatProxyFile
from .get_file_key import get_file_key


async def collect_chat_proxy_files(
    messages: list[Message],
    *,
    run_context: RunContext,
) -> dict[str, ChatProxyFile]:
    """Read the media files the messages refer to, where the caller runs."""
    files: dict[str, ChatProxyFile] = {}
    missing: set[str] = set()

    for message in messages:
        for file_info in message.get_file_infos():
            key = get_file_key(file_info)

            if key is None or key in files or key in missing:
                continue

            file_blob = await get_file_blob(key, run_context=run_context)

            if file_blob is None:
                missing.add(key)
                continue

            files[key] = ChatProxyFile(
                mime_type=file_blob.mime_type,
                base64_data=base64.b64encode(file_blob.raw_data).decode("ascii"),
            )

    return files
