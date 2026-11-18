import json
from collections.abc import Callable
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


def create_model_catalog(
    codex_home: Path,
    model_name: str,
    path: Path,
    list_models: Callable[[], list[dict[str, Any]]] | None = None,
) -> Path:
    """
    Write a one-model catalog for `model_catalog_json`, from the model list Codex
    caches in its home. The cached entry may change with Codex updates.

    The cache holds the list of whichever Codex fetched it last, so an older
    Codex can drop a newer model from it. Then the model is taken from
    `list_models`, the list of the Codex that will run it.
    """
    cache_path = codex_home / "models_cache.json"

    try:
        models = json.loads(cache_path.read_text()).get("models", [])
    except FileNotFoundError as exc:
        if list_models is None:
            raise FileNotFoundError(
                f"Codex has no model list at {cache_path}. Run `codex` once to fetch it."
            ) from exc
        models = []

    entry = _find(models, model_name)

    if entry is None and list_models is not None:
        entry = _find(list_models(), model_name)

    if entry is None:
        raise ValueError(f"Codex's model list at {cache_path} has no {model_name}.")

    path.write_text(json.dumps({"models": [{**entry, **_DIRECT_TOOLS_FIELDS}]}))
    return path


def _find(models: list[dict[str, Any]], model_name: str) -> dict[str, Any] | None:
    return next((m for m in models if m.get("slug") == model_name), None)
