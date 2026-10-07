import json
from pathlib import Path

import pytest

from kiarina.agi.chat_provider_impl.codex_app_server._operations.create_model_catalog import (
    create_model_catalog,
)


def test_create_model_catalog(tmp_path: Path) -> None:
    (tmp_path / "models_cache.json").write_text(
        json.dumps(
            {
                "models": [
                    {"slug": "other"},
                    {
                        "slug": "gpt-test",
                        "context_window": 272_000,
                        "tool_mode": "code_mode_only",
                        "supports_search_tool": True,
                    },
                ]
            }
        )
    )

    path = create_model_catalog(tmp_path, "gpt-test", tmp_path / "models.json")

    [entry] = json.loads(path.read_text())["models"]
    assert entry["slug"] == "gpt-test"
    assert entry["context_window"] == 272_000
    assert entry["tool_mode"] is None
    assert entry["supports_search_tool"] is False


def test_create_model_catalog_errors(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Run `codex` once"):
        create_model_catalog(tmp_path, "gpt-test", tmp_path / "models.json")

    (tmp_path / "models_cache.json").write_text(json.dumps({"models": []}))

    with pytest.raises(ValueError, match="has no gpt-test"):
        create_model_catalog(tmp_path, "gpt-test", tmp_path / "models.json")
