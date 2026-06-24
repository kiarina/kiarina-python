import logging
from typing import Any, Callable, Generic, TypeVar, cast

from kiarina.utils.config_registry import ConfigRegistry

from .._types.object_alias import ObjectAlias
from .._types.object_factory import ObjectFactory
from .._types.object_input import ObjectInput
from .._types.object_name import ObjectName
from .._types.object_specifier import ObjectSpecifier

logger = logging.getLogger(__name__)

TObject = TypeVar("TObject")
TConfig = TypeVar("TConfig")


class ObjectRegistry(Generic[TObject, TConfig]):
    def __init__(
        self,
        *,
        expected_type: type[TObject],
        object_label: str = "Object",
        get_default: Callable[[], ObjectSpecifier | None] | None = None,
        get_aliases: Callable[[], dict[ObjectAlias, ObjectName]] | None = None,
        get_presets: Callable[[], dict[ObjectName, TConfig]] | None = None,
        get_customs: Callable[[], dict[ObjectName, TConfig]] | None = None,
        configure: Callable[[TConfig, dict[str, Any]], TConfig] | None = None,
        factory: ObjectFactory[TObject, TConfig] | None = None,
    ) -> None:
        self._expected_type = expected_type
        self._object_label = object_label
        self._factory = factory or self._default_factory
        self._config_registry = ConfigRegistry[TConfig](
            config_label=f"{object_label} config",
            get_default=get_default,
            get_aliases=get_aliases,
            get_presets=get_presets,
            get_customs=get_customs,
            configure=configure,
        )
        self._registry: dict[ObjectName, TObject] = {}

    def get_default(self) -> ObjectSpecifier | None:
        return self._config_registry.get_default()

    def get_aliases(self) -> dict[ObjectAlias, ObjectName]:
        return self._config_registry.get_aliases()

    def register_config(self, object_name: ObjectName, config: TConfig) -> None:
        self._config_registry.register(object_name, config)

    def unregister_config(self, object_name: ObjectName) -> None:
        self._config_registry.unregister(object_name)

    def clear_configs(self) -> None:
        self._config_registry.clear()

    def is_config_registered(self, object_name: ObjectName) -> bool:
        return self._config_registry.is_registered(object_name)

    def get_config(self, object_specifier: ObjectSpecifier | None = None) -> TConfig:
        return self._config_registry.get(object_specifier)

    def list_aliases(self) -> list[ObjectAlias]:
        return self._config_registry.list_aliases()

    def list_names(self) -> list[ObjectName]:
        return sorted(
            set(self._registry.keys()) | set(self._config_registry.list_names())
        )

    def register(self, object_name: ObjectName, obj: TObject) -> None:
        if not isinstance(obj, self._expected_type):
            raise ValueError(
                f"Registered object is not a {self._expected_type.__name__}"
            )

        if object_name in self._registry:
            logger.warning(
                f"{self._object_label} registry entry is overwritten: {object_name}"
            )

        self._registry[object_name] = obj

    def unregister(self, object_name: ObjectName) -> None:
        self._registry.pop(object_name, None)

    def clear(self) -> None:
        self._registry.clear()

    def is_registered(self, object_name: ObjectName) -> bool:
        return object_name in self._registry

    def get(self, object_name: ObjectName | ObjectAlias | None = None) -> TObject:
        object_name = self._resolve_object_name(object_name)
        obj = self._registry.get(object_name)

        if obj is not None:
            return obj

        obj = self.create(object_name)
        self.register(object_name, obj)
        return obj

    def create(self, object_name: ObjectName, **kwargs: Any) -> TObject:
        resolved_config = self._config_registry.resolve(object_name, **kwargs)
        return self._create(resolved_config.name, resolved_config.config)

    def resolve(
        self, object_input: ObjectInput[TObject] | None = None, **kwargs: Any
    ) -> TObject:
        if isinstance(object_input, self._expected_type):
            return object_input

        if isinstance(object_input, str) or object_input is None:
            resolved_config = self._config_registry.resolve(object_input, **kwargs)
            return self._create(resolved_config.name, resolved_config.config)

        raise ValueError(  # pragma: no cover
            f"Invalid {self._object_label} input: {object_input}. "
            f"Expected an instance of {self._expected_type.__name__} or a string specifier."
        )

    def _create(self, object_name: ObjectName, config: TConfig) -> TObject:
        obj = self._factory(object_name, config)

        if not isinstance(obj, self._expected_type):
            raise ValueError(f"Created object is not a {self._expected_type.__name__}")

        return obj

    def _resolve_object_name(
        self, object_name_or_alias: ObjectName | ObjectAlias | None = None
    ) -> ObjectName:
        if object_name_or_alias is None:
            object_name_or_alias = self.get_default()

            if object_name_or_alias is None:
                raise ValueError("Default is not configured.")

        if "?" in object_name_or_alias:
            raise ValueError("ObjectRegistry.get() does not accept config specifiers.")

        return self.get_aliases().get(object_name_or_alias, object_name_or_alias)

    def _default_factory(self, object_name: ObjectName, config: TConfig) -> TObject:
        create_object = cast(Callable[..., TObject], self._expected_type)

        if isinstance(config, dict):
            return create_object(**config)

        return create_object(config)
