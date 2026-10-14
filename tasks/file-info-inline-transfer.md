# Carry file contents inline in FileInfo for agents whose files live on remote nodes

Done when: a tool running on a remote node can return a FileInfo with its contents inline, the agent caches the contents under a hash-based name and drops the inline data, and files whose `node_id` is set are never read from the agent's own file system.

## Background

An agent (the "brain") can run on a server while its tools run on other machines (the "nodes"), connected peer to peer (for example over a WebRTC data channel), with no shared storage between them. The tools return files as FileInfo, but the bytes are on the node, so the agent cannot read `uri_or_file_path`.

Today:

- `BaseAgent._update_file_infos` reads every file's `uri_or_file_path` where the agent runs. It drops files it cannot read, and rebuilds a file from the agent's own copy if one happens to exist at the same path.
- `BaseAgent._prepare_file_infos` reads `intermediate_file_path` or `uri_or_file_path`. It stores the bytes in the asset repository under `files/<hashed_file_name>` and sets `asset_uri`.
- When rendering for the model, `from_file_info` reads only `asset_uri` if it is set. If that asset is missing, it returns an empty result, so the model loses even the file's metadata. It falls back to `uri_or_file_path` only when `asset_uri` is None.
- `node_id` is a label only; nothing reads it.

## Agreed direction (owner, 2026-10-14; not started)

- Add `base64_text: str | None` to BaseFileInfo: the file's contents, carried inline only while the file travels from the node to the agent.
- `prepared` is False while `base64_text` is set.
- `_prepare_file_infos` takes the bytes from `base64_text` first. It stores them like today (a hash-based name in the asset repository's cache area; `LocalAssetRepository` is enough), sets `asset_uri`, and clears `base64_text`.
- Files with `node_id` set are not read from `uri_or_file_path` in `_update_file_infos` or `_prepare_file_infos`. They are refreshed only when the tool on the node returns a newer FileInfo (via `unique_key`).
- When `asset_uri` points to a missing asset, render the metadata-only XML instead of an empty result. The model can then see that the file existed and read it again.
- A `webrtc://`-style asset repository that fetches lazily from the node is out of scope. Add it later if large files need it. It would also need the asset repository to be chosen by URI scheme; today one repository is resolved per process.

## Open points

- Should the `node_id` rules live in `BaseAgent` (generic) or in the agent that overrides it?
- Who computes `token_count` for files built on the node? Likely the agent rebuilds the FileInfo (`rebuild_file_info`) once it has the bytes.
- Is there a size limit on inline contents? The node would send metadata only above it.
