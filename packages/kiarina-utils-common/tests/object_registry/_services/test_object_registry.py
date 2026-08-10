import logging
from collections.abc import Callable
from typing import cast

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from pydantic_settings_manager import SettingsManager
from pytest import LogCaptureFixture, raises

from kiarina.utils.object_registry import ObjectRegistry


class MyObject:
    def __init__(
        self, message: str = "", options: dict[str, object] | None = None
    ) -> None:
        self.message = message
        self.options = options or {}
        self.name = ""


class MyConfig(BaseModel):
    message: str = ""
    options: dict[str, object] = Field(default_factory=dict)


class MyObjectSettings(BaseSettings):
    default: str = "test1"
    aliases: dict[str, str] = {"default_alias": "test1", "alias2": "test2"}
    presets: dict[str, MyConfig] = {"test1": MyConfig(message="preset")}
    customs: dict[str, MyConfig] = {"test2": MyConfig(message="custom")}


def create_object(name: str, config: MyConfig) -> MyObject:
    obj = MyObject(message=config.message, options=config.options)
    obj.name = name
    return obj


def test_object_registry(caplog: LogCaptureFixture) -> None:
    settings_manager = SettingsManager(MyObjectSettings)

    def configure(config: MyConfig, values: dict[str, object]) -> MyConfig:
        config.options.update(values)
        return config

    registry = ObjectRegistry[MyObject, MyConfig](
        expected_type=MyObject,
        object_label="MyObject",
        get_default=lambda: settings_manager.settings.default,
        get_aliases=lambda: settings_manager.settings.aliases,
        get_presets=lambda: settings_manager.settings.presets,
        get_customs=lambda: settings_manager.settings.customs,
        configure=configure,
        factory=create_object,
    )

    obj = registry.resolve()
    assert isinstance(obj, MyObject)
    assert obj.name == "test1"
    assert obj.message == "preset"

    obj = registry.create("test1")
    assert isinstance(obj, MyObject)
    assert obj.name == "test1"

    obj = registry.resolve("default_alias?mode=fast")
    assert isinstance(obj, MyObject)
    assert obj.name == "test1"
    assert obj.message == "preset"
    assert obj.options == {"mode": "fast"}

    obj = registry.resolve("alias2?mode=fast", level="high")
    assert isinstance(obj, MyObject)
    assert obj.name == "test2"
    assert obj.message == "custom"
    assert obj.options == {"mode": "fast", "level": "high"}

    registered = MyObject(message="registered")
    registry.register("test3", registered)
    assert registry.is_registered("test3")
    assert registry.get("test3") is registered

    aliased = MyObject(message="aliased")
    registry.register("test2", aliased)
    assert registry.get("alias2") is aliased

    fresh = registry.resolve("alias2")
    assert fresh is not aliased
    assert fresh.name == "test2"
    assert fresh.message == "custom"

    obj = registry.resolve(registered)
    assert obj is registered

    with caplog.at_level(logging.WARNING):
        registry.register("test3", MyObject(message="overwritten"))

    assert "MyObject registry entry is overwritten: test3" in caplog.text
    overwritten = registry.get("test3")
    assert overwritten.message == "overwritten"
    assert registry.list_names() == ["test1", "test2", "test3"]
    assert registry.get_default() == "test1"
    assert registry.get_aliases() == {"default_alias": "test1", "alias2": "test2"}
    assert registry.list_aliases() == ["alias2", "default_alias"]

    registry.register_config("test4", MyConfig(message="registered_config"))
    assert registry.is_config_registered("test4")
    assert registry.get_config("test4").message == "registered_config"

    config_obj = registry.get("test4")
    assert config_obj.message == "registered_config"
    assert registry.is_registered("test4")

    registry.unregister_config("test4")
    assert not registry.is_config_registered("test4")
    assert registry.get("test4") is config_obj

    registry.register_config("test5", MyConfig(message="registered_config_2"))
    registry.clear_configs()
    assert not registry.is_config_registered("test5")
    assert registry.is_registered("test4")

    registry.unregister("test3")
    assert not registry.is_registered("test3")
    with raises(ValueError, match="MyObject config is not configured: test3"):
        registry.get("test3")

    registry.unregister("test2")
    assert not registry.is_registered("test2")
    assert registry.get("test2").message == "custom"

    registry.register("test3", registered)
    assert registry.is_registered("test3")
    assert registry.get("test3") is registered

    registry.clear()
    assert not registry.is_registered("test3")
    with raises(ValueError, match="MyObject config is not configured: test3"):
        registry.get("test3")

    singleton = registry.get()
    assert registry.get("test1") is singleton
    assert registry.get("default_alias") is singleton

    with raises(ValueError, match="does not accept config specifiers"):
        registry.get("default_alias?mode=slow")


def test_dict_config() -> None:
    registry = ObjectRegistry[MyObject, dict[str, object]](
        expected_type=MyObject,
        get_presets=lambda: {"test1": {"message": "preset", "level": "normal"}},
        factory=lambda name, config: MyObject(
            message=config["message"], options={"level": config["level"]}
        ),
    )

    obj = registry.create("test1?level=high")

    assert obj.message == "preset"
    assert obj.options == {"level": "high"}


def test_default_factory_with_dict_config() -> None:
    registry = ObjectRegistry[MyObject, dict[str, object]](
        expected_type=MyObject,
        get_presets=lambda: {
            "test1": {"message": "preset", "options": {"level": "normal"}}
        },
    )

    obj = registry.create("test1?message=good")

    assert obj.message == "good"
    assert obj.options == {"level": "normal"}


def test_default_factory_with_object_config() -> None:
    class ConfigObject:
        pass

    class ConfiguredObject:
        def __init__(self, config: ConfigObject) -> None:
            self.config = config

    config = ConfigObject()
    registry = ObjectRegistry[ConfiguredObject, ConfigObject](
        expected_type=ConfiguredObject,
        get_presets=lambda: {"test1": config},
    )

    obj = registry.create("test1")

    assert obj.config is not config
    assert isinstance(obj.config, ConfigObject)


def test_invalid_registered_object() -> None:
    registry = ObjectRegistry[MyObject, MyConfig](
        expected_type=MyObject,
        get_presets=lambda: {"test1": MyConfig()},
        factory=create_object,
    )

    with raises(ValueError, match="Registered object is not a MyObject"):
        registry.register("bad", cast(MyObject, object()))


def test_invalid_created_object() -> None:
    registry = ObjectRegistry[MyObject, MyConfig](
        expected_type=MyObject,
        get_presets=lambda: {"test1": MyConfig()},
        factory=cast(
            Callable[[str, MyConfig], MyObject], lambda name, config: object()
        ),
    )

    with raises(ValueError, match="Created object is not a MyObject"):
        registry.create("test1")
