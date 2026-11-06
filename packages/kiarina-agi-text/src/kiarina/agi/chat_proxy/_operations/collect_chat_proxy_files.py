import base64
import hashlib
from collections.abc import Awaitable, Callable, Collection

from kiarina.agi.file import get_file_blob
from kiarina.agi.message import Message
from kiarina.agi.run_context import RunContext

from .._schemas.chat_proxy_file import ChatProxyFile
from .get_file_key import get_file_key


async def collect_chat_proxy_files(
    messages: list[Message],
    *,
    run_context: RunContext,
    find_missing: Callable[[list[str]], Awaitable[Collection[str]]] | None = None,
) -> dict[str, ChatProxyFile]:
    """
    Collect the media files the messages refer to, where the caller runs.
    `find_missing` gets their hashes and returns the ones the proxy lacks; only
    those carry contents. A file with an `asset_hash` is read only when the proxy
    lacks it. Without `find_missing`, every file carries contents.
    """
    files: dict[str, ChatProxyFile] = {}
    raw_datas: dict[str, bytes] = {}
    unreadable: set[str] = set()

    for message in messages:
        for file_info in message.get_file_infos():
            key = get_file_key(file_info)

            if key is None or key in files or key in unreadable:
                continue

            if file_info.asset_hash is not None:
                files[key] = ChatProxyFile(
                    mime_type=file_info.mime_type, sha256=file_info.asset_hash
                )
                continue

            file_blob = await get_file_blob(key, run_context=run_context)

            if file_blob is None:
                unreadable.add(key)
                continue

            raw_datas[key] = file_blob.raw_data
            files[key] = ChatProxyFile(
                mime_type=file_blob.mime_type,
                sha256=hashlib.sha256(file_blob.raw_data).hexdigest(),
            )

    sha256s = sorted({file.sha256 for file in files.values()})

    if not sha256s:
        return files

    missing = set(sha256s if find_missing is None else await find_missing(sha256s))

    for key, file in list(files.items()):
        if file.sha256 not in missing:
            continue

        raw_data = raw_datas.get(key)

        if raw_data is None:
            file_blob = await get_file_blob(key, run_context=run_context)

            if file_blob is None:
                # The proxy lacks it and it cannot be read here: metadata only.
                del files[key]
                continue

            raw_data = file_blob.raw_data

        files[key] = file.model_copy(
            update={"base64_data": base64.b64encode(raw_data).decode("ascii")}
        )

    return files
