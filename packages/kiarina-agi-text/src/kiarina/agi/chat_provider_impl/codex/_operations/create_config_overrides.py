from pathlib import Path

import tomllib

from .._constants.disabled_features import DISABLED_FEATURES, DISABLED_INSTRUCTIONS


def create_config_overrides(codex_home: Path, model_catalog_path: Path) -> list[str]:
    """
    `--config` overrides that leave only the caller's instructions and tools.

    They must be given when the process starts: `thread/start` ignores features
    and `model_catalog_json`. The MCP servers in the user's `config.toml` are
    turned off one by one.
    """
    overrides = [f"features.{feature}=false" for feature in DISABLED_FEATURES]
    overrides.append('web_search="disabled"')
    overrides += [f"{key}=false" for key in DISABLED_INSTRUCTIONS]

    config_path = codex_home / "config.toml"

    if config_path.is_file():
        config = tomllib.loads(config_path.read_text())

        for name in config.get("mcp_servers", {}):
            overrides.append(f"mcp_servers.{name}.enabled=false")

    overrides.append(f"model_catalog_json={_toml_string(str(model_catalog_path))}")
    return overrides


def _toml_string(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
