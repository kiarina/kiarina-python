# Run Context and Registries

How components stay stateless so one process can serve many users and agents.

## RunContext Is Passed Explicitly

`RunContext` travels as an argument from `run_agent` through the workflow, prompt, and tool
layers (`AgentContext`, `StateContext`, `SectionContext`, `ToolContext`). There is no
context variable. A component reads the identity from the `RunContext` it receives and
holds none of its own.

| Field | Meaning |
| --- | --- |
| `organization_id`, `user_id`, `agent_id` | Whose data this run works on. Repository paths are built from them. |
| `runner_id` | Who is running the agent. A new ULID for each `RunContext` unless given. Not read from settings. |
| `timezone`, `language`, `currency` | Presentation of the run. |
| `metadata` | Trace values added with `with_metadata()`, which returns a copy. |

`RunContextSettings` only supplies defaults for the identity fields of `RunContext()`.
A process that serves several users or agents must build each `RunContext` explicitly.
Set `disallow_default_ids` there: a call path that falls back to `RunContext()` then
raises instead of silently using the process-wide default.

## Files and Where They Live

`FileInfo.node_id` marks the node a file comes from, and is `None` for files not bound to
one. It is unrelated to `runner_id`.

`BaseAgent._update_file_infos` and `_prepare_file_infos` assume the files are readable
where the agent loop runs. An agent whose files live elsewhere overrides them.

## Choosing How to Hold a Component

| The component | Hold it as |
| --- | --- |
| has no state and one implementation | a plain class, constructed where it is used |
| has no state and needs replaceable infrastructure | a `ComponentRegistry` entry; every `resolve` builds a new instance |
| has state (a client holding connections, a loaded model, a per-agent runtime) | an `ObjectRegistry` entry; `get(name)` returns one instance per name |

A registry factory can inject the `RunContext` into the new instance
(`asset_repository_registry` does). Do not bind a user or agent into a registered factory:
the registry is process-wide, so the last registration wins.

## Tools

`tool_registry` is a `ComponentRegistry`, and a tool named in `ToolOptions.tools` is
created for each call. Write tools without state: read the identity from
`ToolContext.run_context`, and look up anything that must outlive the call in an
`ObjectRegistry`. A `Tool` instance may also be passed in `ToolOptions.tools`; keep it
stateless as well, because callers may share it across runs.
