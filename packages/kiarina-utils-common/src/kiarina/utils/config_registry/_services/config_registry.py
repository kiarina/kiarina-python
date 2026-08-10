import copy
import logging
from collections.abc import Callable
from typing import Any, Generic, TypeVar, cast

from pydantic import BaseModel

from kiarina.utils.common import parse_config_string

from .._types.config_alias import ConfigAlias
from .._types.config_name import ConfigName
from .._types.config_specifier import ConfigSpecifier
from .._views.resolved_config import ResolvedConfig

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ConfigRegistry(Generic[T]):
    def __init__(
        self,
        *,
        config_label: str = "Config",
        get_default: Callable[[], ConfigSpecifier | None] | None = None,
        get_aliases: Callable[[], dict[ConfigAlias, ConfigName]] | None = None,
        get_presets: Callable[[], dict[ConfigName, T]] | None = None,
        get_customs: Callable[[], dict[ConfigName, T]] | None = None,
        configure: Callable[[T, dict[str, Any]], T] | None = None,
    ) -> None:
        self._config_label = config_label
        self._get_default = get_default
        self._get_aliases = get_aliases
        self._get_presets = get_presets
        self._get_customs = get_customs
        self._configure = configure or self._default_configure
        self._registry: dict[ConfigName, T] = {}

    def get_default(self) -> ConfigSpecifier | None:
        return self._get_default() if self._get_default else None

    def get_aliases(self) -> dict[ConfigAlias, ConfigName]:
        aliases = self._get_aliases() if self._get_aliases else {}
        return dict(aliases)

    def list_aliases(self) -> list[ConfigAlias]:
        return sorted(self.get_aliases().keys())

    def list_names(self) -> list[ConfigName]:
        customs = self._get_customs() if self._get_customs else {}
        presets = self._get_presets() if self._get_presets else {}
        return sorted(
            set(self._registry.keys()) | set(customs.keys()) | set(presets.keys())
        )

    def register(self, config_name: ConfigName, config: T) -> None:
        if config_name in self._registry:
            logger.warning(
                f"{self._config_label} registry entry is overwritten: {config_name}"
            )

        self._registry[config_name] = config

    def unregister(self, config_name: ConfigName) -> None:
        self._registry.pop(config_name, None)

    def is_registered(self, config_name: ConfigName) -> bool:
        return config_name in self._registry

    def clear(self) -> None:
        self._registry.clear()

    def get(
        self,
        config_specifier: ConfigSpecifier | None = None,
        **kwargs: Any,
    ) -> T:
        return self.resolve(config_specifier, **kwargs).config

    def resolve(
        self,
        config_specifier: ConfigSpecifier | None = None,
        **kwargs: Any,
    ) -> ResolvedConfig[T]:
        config_name, specifier_kwargs = self._resolve_name_and_kwargs(config_specifier)

        config = self._get_config(config_name)

        if specifier_kwargs:
            config = self._configure(config, specifier_kwargs)

        if kwargs:
            config = self._configure(config, kwargs)

        return ResolvedConfig(config_name, config)

    def _resolve_name_and_kwargs(
        self, config_specifier: ConfigSpecifier | None = None
    ) -> tuple[ConfigName, dict[str, Any]]:
        if config_specifier is None:
            config_specifier = self.get_default()

            if config_specifier is None:
                raise ValueError("Default is not configured.")

        if "?" in config_specifier:
            name_or_alias, config_string = config_specifier.split("?", 1)
            kwargs = parse_config_string(
                config_string, separator="&", key_value_separator="="
            )
        else:
            name_or_alias = config_specifier
            kwargs = {}

        aliases = self._get_aliases() if self._get_aliases else {}
        config_name = aliases.get(name_or_alias, name_or_alias)

        return config_name, kwargs

    def _get_config(self, config_name: ConfigName) -> T:
        customs = self._get_customs() if self._get_customs else {}
        presets = self._get_presets() if self._get_presets else {}

        if config_name in self._registry:
            config = self._registry[config_name]
        elif config_name in customs:
            config = customs[config_name]
        elif config_name in presets:
            config = presets[config_name]
        else:
            raise ValueError(f"{self._config_label} is not configured: {config_name}")

        return self._copy_config(config)

    def _copy_config(self, config: T) -> T:
        if isinstance(config, BaseModel):
            return cast(T, config.model_copy(deep=True))

        return copy.deepcopy(config)

    def _default_configure(self, config: T, values: dict[str, Any]) -> T:
        if isinstance(config, BaseModel):
            return cast(
                T, type(config).model_validate({**config.model_dump(), **values})
            )

        if isinstance(config, dict):
            return cast(T, {**config, **values})

        raise TypeError(
            f"Default configure does not support {type(config).__name__}. "
            "Pass configure=... to ConfigRegistry."
        )
