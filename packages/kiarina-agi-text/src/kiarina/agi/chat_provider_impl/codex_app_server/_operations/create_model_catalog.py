import json
from pathlib import Path
from typing import Any

_DIRECT_TOOLS_FIELDS: dict[str, Any] = {
    "tool_mode": None,
    "multi_agent_version": None,
    "apply_patch_tool_type": None,
    "supports_search_tool": False,
    "experimental_supported_tools": [],
    "include_skills_usage_instructions": False,
    "include_apps_usage_instructions": False,
    "include_plugin_usage_instructions": False,
    "node_repl_disabled": True,
}
"""
New models only call tools from inside a JavaScript cell (`tool_mode:
code_mode_only`). Neither features nor thread config change it, so the model
entry itself is rewritten to pass the tools as plain functions.
"""


def create_model_catalog(codex_home: Path, model_name: str, path: Path) -> Path:
    """
    Write a one-model catalog for `model_catalog_json`, from the model list Codex
    caches in its home. The cached entry may change with Codex updates.
    """
    cache_path = codex_home / "models_cache.json"

    try:
        cache = json.loads(cache_path.read_text())
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"Codex has no model list at {cache_path}. Run `codex` once to fetch it."
        ) from exc

    for model in cache.get("models", []):
        if model.get("slug") == model_name:
            entry = {**model, **_DIRECT_TOOLS_FIELDS}
            break
    else:
        raise ValueError(f"Codex's model list at {cache_path} has no {model_name}.")

    path.write_text(json.dumps({"models": [entry]}))
    return path
