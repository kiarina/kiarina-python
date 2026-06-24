from typing import Any

from kiarina.utils.common import ImportPath
from pydantic_settings import BaseSettings
from pydantic_settings_manager import SettingsManager

from kiarina.utils.component_registry import ComponentFactory, ComponentRegistry


class MyClass:
    def __init__(self, message: str = ""):
        self.message = message
        self.name = ""


class SubMyClass(MyClass):
    pass


def create_sub_my_class(message: str = "") -> SubMyClass:
    return SubMyClass(message)


def _factory_wrapper(
    factory: ComponentFactory[MyClass],
    component_name: str,
    *args: Any,
    **kwargs: Any,
) -> MyClass:
    instance = factory(*args, **kwargs)
    instance.name = component_name
    return instance


class MyClassSettings(BaseSettings):
    default: str = "test1"
    aliases: dict[str, str] = {"alias1": "test1", "alias2": "test2"}
    presets: dict[str, ImportPath] = {"test1": f"{__name__}:SubMyClass"}
    customs: dict[str, ImportPath] = {
        "test2": f"{__name__}:SubMyClass",
        "test4": f"{__name__}:create_sub_my_class",
    }


def test_component_registry() -> None:
    settings_manager = SettingsManager(MyClassSettings)

    registry = ComponentRegistry(
        expected_type=MyClass,
        get_default=lambda: settings_manager.settings.default,
        get_aliases=lambda: settings_manager.settings.aliases,
        get_presets=lambda: settings_manager.settings.presets,
        get_customs=lambda: settings_manager.settings.customs,
        factory_wrapper=_factory_wrapper,
    )

    assert isinstance(registry.resolve(), SubMyClass)
    assert isinstance(registry.create("test1"), SubMyClass)
    assert isinstance(registry.resolve("test1"), SubMyClass)

    instance = registry.resolve("alias1")
    assert isinstance(instance, SubMyClass)
    assert instance.name == "test1"

    instance = registry.resolve("alias2?message=good")
    assert isinstance(instance, SubMyClass)
    assert instance.name == "test2"
    assert instance.message == "good"

    instance = registry.resolve("test2?message=good")
    assert isinstance(instance, SubMyClass)
    assert instance.message == "good"

    instance = registry.resolve("test4?message=factory")
    assert isinstance(instance, SubMyClass)
    assert instance.name == "test4"
    assert instance.message == "factory"

    registry.register("test3", SubMyClass)
    assert registry.get("test3") == SubMyClass

    instance = registry.resolve("test3?message=hello")
    assert isinstance(instance, SubMyClass)
    assert instance.name == "test3"
    assert instance.message == "hello"

    instance = registry.resolve(instance)
    assert isinstance(instance, SubMyClass)

    registry.unregister("test3")
    assert registry.get("test3") is None

    registry.register("test3", SubMyClass)
    assert registry.get("test3") == SubMyClass
    assert registry.get_default() == "test1"
    assert registry.get_aliases() == {"alias1": "test1", "alias2": "test2"}
    assert registry.list_aliases() == ["alias1", "alias2"]
    assert registry.list_names() == ["test1", "test2", "test3", "test4"]

    registry.clear()
    assert registry.get("test3") is None
