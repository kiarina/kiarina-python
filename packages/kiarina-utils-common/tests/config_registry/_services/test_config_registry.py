import logging
from typing import Any

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from pydantic_settings_manager import SettingsManager
from pytest import LogCaptureFixture, raises

from kiarina.utils.config_registry import ConfigRegistry, ResolvedConfig


def test_base_model(caplog: LogCaptureFixture) -> None:
    class MyConfig(BaseModel):
        message: str = ""
        options: dict[str, str] = Field(default_factory=dict)

    class MyClassSettings(BaseSettings):
        default: str = "default_alias"
        aliases: dict[str, str] = {"default_alias": "test1"}
        presets: dict[str, MyConfig] = {"test1": MyConfig(message="preset")}
        customs: dict[str, MyConfig] = {"test2": MyConfig(message="custom")}

    settings_manager = SettingsManager(MyClassSettings)

    registry = ConfigRegistry(
        get_default=lambda: settings_manager.settings.default,
        get_aliases=lambda: settings_manager.settings.aliases,
        get_presets=lambda: settings_manager.settings.presets,
        get_customs=lambda: settings_manager.settings.customs,
    )

    config = registry.get()
    assert config.message == "preset"

    resolved = registry.resolve("default_alias?message=good")
    assert resolved == ResolvedConfig("test1", MyConfig(message="good"))
    assert resolved.name == "test1"
    assert resolved.config.message == "good"

    name, config = registry.resolve("test2")
    assert name == "test2"
    assert config.message == "custom"

    registry.register("test3", MyConfig(message="registered"))
    assert registry.is_registered("test3")

    resolved = registry.resolve("test3?message=hello")
    assert resolved.name == "test3"
    assert resolved.config.message == "hello"

    config = registry.get("test3?message=hello", message="good")
    assert config.message == "good"

    with caplog.at_level(logging.WARNING):
        registry.register("test3", MyConfig(message="overwritten"))

    assert "Config registry entry is overwritten: test3" in caplog.text
    assert registry.get("test3") == MyConfig(message="overwritten")

    registry.unregister("test3")
    assert not registry.is_registered("test3")

    registry.register("test3", MyConfig(message="registered"))
    assert registry.get("test3") == MyConfig(message="registered")
    assert registry.get_default() == "default_alias"
    assert registry.get_aliases() == {"default_alias": "test1"}
    assert registry.list_aliases() == ["default_alias"]
    assert registry.list_names() == ["test1", "test2", "test3"]

    registry.clear()
    assert not registry.is_registered("test3")


def test_configure() -> Any:
    class MyConfig(BaseModel):
        message: str = ""
        options: dict[str, str] = Field(default_factory=dict)

    class MyClassSettings(BaseSettings):
        presets: dict[str, MyConfig] = {"test1": MyConfig(message="preset")}

    settings_manager = SettingsManager(MyClassSettings)

    def configure(config: MyConfig, values: dict[str, Any]) -> MyConfig:
        config.options.update(values)
        return config

    registry = ConfigRegistry(
        get_presets=lambda: settings_manager.settings.presets,
        configure=configure,
    )

    config = registry.get("test1?mode=fast", level="high")

    assert config.message == "preset"
    assert config.options == {"mode": "fast", "level": "high"}


def test_dict() -> None:
    presets: dict[str, dict[str, object]] = {
        "test1": {"message": "preset", "options": {"mode": "normal"}}
    }

    registry = ConfigRegistry[dict[str, object]](
        get_presets=lambda: presets,
    )

    config = registry.get("test1?message=good", level="high")

    assert config == {
        "message": "good",
        "options": {"mode": "normal"},
        "level": "high",
    }

    assert presets["test1"] == {"message": "preset", "options": {"mode": "normal"}}

    config["options"] = {"mode": "changed"}

    assert registry.get("test1") == {
        "message": "preset",
        "options": {"mode": "normal"},
    }


def test_unsupported_config_type() -> Any:
    registry = ConfigRegistry[int](
        get_presets=lambda: {"test1": 1},
    )

    with raises(TypeError, match="Pass configure=\\.\\.\\. to ConfigRegistry"):
        registry.get("test1?value=2")

    def configure(config: int, values: dict[str, Any]) -> int:
        return config + int(values.get("value", 0))

    registry = ConfigRegistry[int](
        get_presets=lambda: {"test1": 1},
        configure=configure,
    )

    config = registry.get("test1?value=2")
    assert config == 3


def test_unconfigured() -> None:
    registry = ConfigRegistry[dict[str, object]](config_label="Profile")

    with raises(ValueError, match="Default is not configured"):
        registry.get()

    with raises(ValueError, match="Profile is not configured: missing"):
        registry.get("missing")
