import logging
from typing import Any, Callable, Generic, TypeVar, cast

from kiarina.utils.common import ImportPath, import_object, parse_config_string

from .._types.component_alias import ComponentAlias
from .._types.component_factory import ComponentFactory
from .._types.component_input import ComponentInput
from .._types.component_name import ComponentName
from .._types.component_specifier import ComponentSpecifier

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ComponentRegistry(Generic[T]):
    def __init__(
        self,
        *,
        expected_type: type[T],
        component_label: str = "Component",
        get_default: Callable[[], ComponentSpecifier | None] | None = None,
        get_aliases: Callable[[], dict[ComponentAlias, ComponentName]] | None = None,
        get_presets: Callable[[], dict[ComponentName, ImportPath]] | None = None,
        get_customs: Callable[[], dict[ComponentName, ImportPath]] | None = None,
        factory_wrapper: Callable[[ComponentFactory[T], ComponentName, Any], T]
        | None = None,
    ) -> None:
        self._expected_type = expected_type
        self._component_label = component_label
        self._get_default = get_default
        self._get_aliases = get_aliases
        self._get_presets = get_presets
        self._get_customs = get_customs
        self._factory_wrapper = factory_wrapper
        self._registry: dict[ComponentName, ComponentFactory[T]] = {}

    def get_default(self) -> ComponentSpecifier | None:
        return self._get_default() if self._get_default else None

    def get_aliases(self) -> dict[ComponentAlias, ComponentName]:
        aliases = self._get_aliases() if self._get_aliases else {}
        return dict(aliases)

    def list_aliases(self) -> list[ComponentAlias]:
        return sorted(self.get_aliases().keys())

    def list_names(self) -> list[ComponentName]:
        customs = self._get_customs() if self._get_customs else {}
        presets = self._get_presets() if self._get_presets else {}
        return sorted(
            set(self._registry.keys()) | set(customs.keys()) | set(presets.keys())
        )

    def register(
        self, component_name: ComponentName, factory: ComponentFactory[T]
    ) -> None:
        if component_name in self._registry:
            logger.warning(
                f"{self._component_label} registry entry is overwritten: {component_name}"
            )

        self._registry[component_name] = factory

    def unregister(self, component_name: ComponentName) -> None:
        self._registry.pop(component_name, None)

    def get(self, component_name: ComponentName) -> ComponentFactory[T] | None:
        return self._registry.get(component_name)

    def clear(self) -> None:
        self._registry.clear()

    def create(self, component_name: ComponentName, *args: Any, **kwargs: Any) -> T:
        factory = self._get_component_factory(component_name)

        if self._factory_wrapper is not None:
            instance = self._factory_wrapper(factory, component_name, *args, **kwargs)
        else:
            instance = factory(*args, **kwargs)

        if not isinstance(instance, self._expected_type):
            raise ValueError(f"Created object is not a {self._expected_type.__name__}")

        return instance

    def resolve(
        self,
        component_input: ComponentInput[T] | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> T:
        if isinstance(component_input, self._expected_type):
            return component_input

        if isinstance(component_input, str) or component_input is None:
            component_name, specifier_kwargs = self._resolve_name_and_kwargs(
                component_input
            )

            if specifier_kwargs:
                kwargs.update(specifier_kwargs)

            return self.create(component_name, *args, **kwargs)

        raise ValueError(  # pragma: no cover
            f"Invalid {self._component_label} input: {component_input}. "
            f"Expected an instance of {self._expected_type.__name__} or a string specifier."
        )

    def _resolve_name_and_kwargs(
        self, component_specifier: ComponentSpecifier | None = None
    ) -> tuple[ComponentName, dict[str, Any]]:
        if component_specifier is None:
            component_specifier = self.get_default()

            if component_specifier is None:
                raise ValueError("Default is not configured.")

        if "?" in component_specifier:
            name_or_alias, config_string = component_specifier.split("?", 1)
            kwargs = parse_config_string(
                config_string, separator="&", key_value_separator="="
            )
        else:
            name_or_alias = component_specifier
            kwargs = {}

        aliases = self._get_aliases() if self._get_aliases else {}
        component_name = aliases.get(name_or_alias, name_or_alias)

        return component_name, kwargs

    def _get_component_factory(
        self, component_name: ComponentName
    ) -> ComponentFactory[T]:
        factory = self._registry.get(component_name)

        if factory is not None:
            return factory

        customs = self._get_customs() if self._get_customs else {}
        presets = self._get_presets() if self._get_presets else {}

        if component_name in customs:
            return cast(ComponentFactory[T], import_object(customs[component_name]))

        if component_name in presets:
            return cast(ComponentFactory[T], import_object(presets[component_name]))

        raise ValueError(f"{self._component_label} is not registered: {component_name}")
