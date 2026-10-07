from pathlib import Path

from kiarina.agi.chat_provider_impl.codex_app_server._operations.create_config_overrides import (
    create_config_overrides,
)


def test_create_config_overrides(tmp_path: Path) -> None:
    (tmp_path / "config.toml").write_text(
        '[mcp_servers.blender]\ncommand = "x"\n\n[mcp_servers.aseprite]\nurl = "y"\n'
    )

    overrides = create_config_overrides(tmp_path, Path('/tmp/a "b"/models.json'))

    assert "features.shell_tool=false" in overrides
    assert 'web_search="disabled"' in overrides
    assert "include_environment_context=false" in overrides
    assert "mcp_servers.blender.enabled=false" in overrides
    assert "mcp_servers.aseprite.enabled=false" in overrides
    assert overrides[-1] == 'model_catalog_json="/tmp/a \\"b\\"/models.json"'


def test_create_config_overrides_without_config(tmp_path: Path) -> None:
    overrides = create_config_overrides(tmp_path, tmp_path / "models.json")

    assert not any(o.startswith("mcp_servers.") for o in overrides)
