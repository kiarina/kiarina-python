NO_FORCED_TOOL_CHOICE_MODEL_PREFIXES: tuple[str, ...] = (
    "claude-fable-5-1",
    "claude-fable-5-2",
    "claude-opus-5-5",
    "claude-sonnet-5-5",
)
"""Models that reject `tool_choice` of type `any` or `tool` with a 400."""
