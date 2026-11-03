# kiarina-agi-flow

[![PyPI](https://img.shields.io/pypi/v/kiarina-agi-flow.svg)](https://pypi.org/project/kiarina-agi-flow/)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](../../LICENSE)

> [!NOTE] What is this?
> `kiarina-agi-flow` provides prompt, section, state, and workflow orchestration for AI agents.

## Dependencies

| Package | Version | License |
| --- | --- | --- |
| [kiarina-agi-base](../kiarina-agi-base/) | `>=2.7.0` | MIT |
| [kiarina-agi-data](../kiarina-agi-data/) | `>=2.7.0` | MIT |
| [kiarina-agi-text](../kiarina-agi-text/) | `>=2.8.0` | MIT |
| [kiarina-i18n](../kiarina-i18n/) | `>=2.3.1` | MIT |
| [kiarina-utils-common](../kiarina-utils-common/) | `>=2.8.0` | MIT |
| [Pydantic](https://github.com/pydantic/pydantic) | `>=2.11.7,<3` | MIT |
| [pydantic-settings](https://github.com/pydantic/pydantic-settings) | `>=2.10.1,<3` | MIT |
| [pydantic-settings-manager](https://github.com/kiarina/pydantic-settings-manager) | `>=3.2.0` | MIT |


## Installation

```sh
pip install kiarina-agi-flow
```

## Features

### Temporary prompt resizing

A prompt composes fixed and resizable sections in a `SectionContainer`. The container
subtracts fixed sections and distributes the remaining token allowance among resizable
sections by weight. `HistorySection` shrinks its file view before removing old message
units; `FileInfoSection` shrinks files before removing them from its view. These operations
change the section's presentation, not the supplied `History`.

`run_prompt` retains the original `ChatLimits` and computes an effective limit from the
current token conversion factor. Local resize iterations do not compound that factor.
Provider token-overflow responses can recalibrate it from the estimated and reported
counts. When no actual count is reported, retrying reduces the current allowance.

A resize may advance a section's internal state without reducing its token count on that
call. The prompt does not stop on one unchanged count and does not impose a local resize
iteration limit. Each section must exhaust its finite resizing stages and return `False`
from `is_resizable()` when it cannot resize further.

If the remaining sections cannot fit, including when fixed sections alone exceed the
allowance, `TokenOverflowError` propagates to the caller. Persistent compaction is the
caller's responsibility; it is not an implicit mutation performed by the prompt.

### Migrating custom sections

Subclasses of `BaseSection` must override `_resize`, not `resize`. The public wrapper
invalidates cached estimates in `finally`, including on failure, cancellation, or closure
of the async generator. Static and tool sections retain the non-resizable default.
Classes implementing the `Section` protocol without inheriting `BaseSection` must provide
the same cache-invalidation and finite-resize behavior themselves.

## API Reference

### `kiarina.agi.section.BaseSection`

Relevant resizing methods:

```python
def is_resizable(self) -> bool: ...
async def resize(self, reduce: TokenCount) -> AsyncIterator[Event]: ...
async def _resize(self, reduce: TokenCount) -> AsyncIterator[Event]: ...
def get_estimates(self, ignore_cache: bool = False) -> ChatEstimates: ...
```

`reduce` is the requested reduction in estimated tokens, not a target size. Call `resize`
and fully consume its events; implement the protected `_resize` hook in subclasses.
`get_estimates()` caches until the view is resized. `ignore_cache=True` remains available
for other explicit view changes, but is not required after the resize wrapper completes.

### `kiarina.agi.section_container.SectionContainer`

```python
def __init__(
    self,
    ctx: SectionContext,
    *,
    sections: list[Section | tuple[Section, Weight]] | None = None,
) -> None: ...
def is_resizable(self) -> bool: ...
async def resize(self, token_count_limit: int) -> AsyncIterator[Event]: ...
def get_estimates(self, ignore_cache: bool = False) -> ChatEstimates: ...
```

Unlike a section, the container's `resize` accepts the desired total token limit.
Fixed sections are retained. An impossible fixed-section budget raises
`kiarina.agi.chat_provider.TokenOverflowError`, rather than `ValueError`. For local
capacity failures, its `limit` is the effective local token allowance. Provider-originated
errors may instead report the provider's token units.

### `kiarina.agi.prompt.run_prompt`

```python
async def run_prompt(
    history: History,
    *,
    chat_options: ChatOptions | None = None,
    prompt_options: PromptOptions | None = None,
    cost_recorder: CostRecorder | None = None,
    run_context: RunContext,
    **kwargs: Any,
) -> AsyncIterator[Event]: ...
```

`prompt_options["limits"]` accepts `ChatLimits` or a limits specifier. If omitted, model
capabilities supply the limits. Provider overflow retries are separate from section
resize iterations. Neither the supplied limits object nor the stored history is changed
by temporary resizing.
