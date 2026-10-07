from collections.abc import Mapping

_CLEARED_PREFIXES = ("ANTHROPIC_", "CLAUDE_CODE_")

_KEPT_KEYS = frozenset({"CLAUDE_CODE_ENTRYPOINT"})
"""Set by the SDK itself."""


def create_child_env(
    inherited: Mapping[str, str], overrides: Mapping[str, str]
) -> dict[str, str]:
    """
    Environment for Claude Code, which the SDK merges over the inherited one.

    Inherited `ANTHROPIC_*` and `CLAUDE_CODE_*` variables are cleared, so Claude
    Code uses its own login. Otherwise an API key would bill the API, and a host
    Claude Code session would lend its credentials. `overrides` are applied last.
    """
    env = {
        key: ""
        for key in inherited
        if key.startswith(_CLEARED_PREFIXES) and key not in _KEPT_KEYS
    }
    env.update(overrides)
    return env
