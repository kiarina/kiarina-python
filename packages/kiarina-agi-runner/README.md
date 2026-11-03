# kiarina-agi-runner

## What is this?

`kiarina-agi-runner` provides agent execution, task runners, and structured output helpers for AI agents.

## Dependencies

| Package | Version | License |
| --- | --- | --- |
| [kiarina-agi-base](../kiarina-agi-base/) | `>=2.7.0` | MIT |
| [kiarina-agi-data](../kiarina-agi-data/) | `>=2.7.0` | MIT |
| [kiarina-agi-data-builder](../kiarina-agi-data-builder/) | `>=2.13.0` | MIT |
| [kiarina-agi-file](../kiarina-agi-file/) | `>=2.8.0` | MIT |
| [kiarina-agi-flow](../kiarina-agi-flow/) | `>=2.11.0` | MIT |
| [kiarina-agi-text](../kiarina-agi-text/) | `>=2.8.0` | MIT |
| [kiarina-agi-tool](../kiarina-agi-tool/) | `>=2.12.0` | MIT |
| [kiarina-utils-common](../kiarina-utils-common/) | `>=2.8.0` | MIT |
| [kiarina-utils-file](../kiarina-utils-file/) | `>=2.3.1` | MIT |
| [Pydantic](https://github.com/pydantic/pydantic) | `>=2.11.7,<3` | MIT |
| [pydantic-settings](https://github.com/pydantic/pydantic-settings) | `>=2.10.1,<3` | MIT |
| [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) | `>=3.2.0` | MIT |

## Structured output

```python
from kiarina.agi.structured_output import generate_model

async def generate_model(
    history_input: HistoryInput,
    python_schema: type[T],
    *,
    chat_options: ChatOptions | None = None,
    prompt_options: PromptOptions | None = None,
    cost_recorder: CostRecorder | None = None,
    run_context: RunContext,
    **kwargs: Any,
) -> T: ...
```

`T` is a Pydantic `BaseModel`. The helper presents its schema as a tool and validates
arguments from the first tool call in the final AI message using `model_validate_json()`.
JSON arrays and date strings therefore work with strict tuple and date fields, while
invalid values still raise `ValidationError`. Additional tool calls are ignored; an invalid
first call is not replaced by a later one. The helper does not execute tools or retry validation.

Pass a custom Prompt through `prompt_options` to control Sections and input presentation.
That Prompt must expose the generated tool definition in `history.tool_infos`, for example
with `ToolSection`. The default Prompt is `vanilla`.

A string, event list, or history specification creates a new History. Passing an existing
History reuses it and replaces its `tool_infos`; use a copy if those definitions must be
preserved. Supplied nonempty option dictionaries are also modified (`tool_choice="any"`,
`streaming=False`, and the default Prompt when absent). Model/provider support determines
whether tool choice can be enforced; see the [remaining work](../../tasks/structured-output-via-json-output.md).
