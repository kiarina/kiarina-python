# Replace node_id with runner_id

## Goal

Remove `node_id` from `RunContext` and settings, add `RunContext.runner_id`, and make
`FileInfo.node_id` an optional origin marker. Release it so kiari, kiari-plugins, and
Spirits Garden Brain can follow.

## Background

`RunContext.runner_id` was renamed to `node_id` when Spirits Garden Body ran the agent loop
and needed to carry a body ID. The Brain now runs the agent loop, so that rename mixed two
concepts. Agreed with the owner on 2026-09-30:

- `RunContext.node_id` is only displayed (`format_run_context`, kiari loggers and console).
  Logic uses `get_node_id()` from settings instead.
- `runner_id` is the executing runner. Spirits Garden Brain will host many Spirits in one
  process and use `runner_id` as the lease holder of each Spirit run.
- `FileInfo.node_id` keeps its name. It marks where a file lives (a Body). Files not bound
  to a Body use `None`.
- `BaseAgent._update_file_infos` assumes the files live where the agent loop runs (kiari).
  Drop the node check and treat every file as local. Agents running elsewhere override it
  (Spirits Garden `tasks/brain-agent-file-infos.md`).

## Changes

- kiarina-agi-base
  - `RunContext`: remove `node_id`, add `runner_id: IDStr` defaulting to a new ULID.
    Not read from settings.
  - Settings: remove `node_id`. Remove `get_node_id()` and the `node_id` case of `get_id`.
  - `format_run_context`: show `runner_id`.
  - Add the ULID dependency (`ulid-py`, already used by kiarina-agi-data).
- kiarina-agi-data
  - `BaseFileInfo.node_id: str | None = None` (no default factory).
- kiarina-agi-runner
  - `BaseAgent._update_file_infos`: remove the node filter; process all file infos.
- Tests: conftests pass `runner_id` instead of `node_id`; update run_context and base_agent tests.
- READMEs: kiarina-agi-base (`get_node_id`, `RunContext`, settings), kiarina-agi-data (`FileInfo`).
- `packages/kiarina-agi-text/scripts/_common.py`: `node_id="scripts"` → `runner_id`.
- Breaking change. Record it in CHANGELOG and release (`docs/runbooks/release.md`).

## Compatibility

- `RunContext` is not serialized anywhere found, so no alias is needed.
- Stored histories keep `FileInfo.node_id` values (old machine IDs, `"brain"`). They still load.

## Follow-ups (other repositories)

- kiari: `tasks/runner-id.md` (rename `RunOptions.node_id`, CLI option, loggers, remove `node_id.txt`; includes kiari-plugins)
- Spirits Garden Brain: `tasks/brain-multi-spirit-host.md` (pass `runner_id`; add a pass-through `BrainAgent._update_file_infos` in the same change that bumps kiarina)
