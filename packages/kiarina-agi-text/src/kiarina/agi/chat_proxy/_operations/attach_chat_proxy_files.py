import base64
import hashlib
import os

from kiarina.agi.asset_repository import create_asset_repository
from kiarina.agi.file_info import FileInfo
from kiarina.agi.message import Message
from kiarina.agi.run_context import RunContext

from .._schemas.chat_proxy_file import ChatProxyFile
from .get_file_key import get_file_key


async def attach_chat_proxy_files(
    messages: list[Message],
    files: dict[str, ChatProxyFile],
    *,
    run_context: RunContext,
) -> list[Message]:
    """
    Store the sent file contents in the chat proxy's asset repository and point the
    files at them. A media file sent without contents becomes metadata only: its
    path names a file on the caller's machine, not on the proxy's.
    """
    asset_repository = create_asset_repository(run_context)
    asset_uris: dict[str, str] = {}

    for key, file in files.items():
        raw_data = base64.b64decode(file.base64_data)
        file_hash = hashlib.sha256(raw_data).hexdigest()
        asset_uri = asset_repository.generate_cache_uri(
            os.path.join("chat_proxy", file_hash)
        )
        await asset_repository.set(
            asset_uri, file.mime_type, raw_data, only_not_exists=True
        )
        asset_uris[key] = asset_uri

    def attach(file_info: FileInfo) -> FileInfo:
        key = get_file_key(file_info)

        if key is None:
            return file_info

        if key in asset_uris:
            return file_info.model_copy(update={"asset_uri": asset_uris[key]})

        return file_info.model_copy(update={"metadata_only": True})

    new_messages: list[Message] = []

    for message in messages:
        new_contents = [
            content.model_copy(update={"files": [attach(fi) for fi in content.files]})
            if content.files
            else content
            for content in message.contents
        ]
        new_messages.append(message.model_copy(update={"contents": new_contents}))

    return new_messages
