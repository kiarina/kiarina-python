from importlib.metadata import version

from ._services.config_registry import ConfigRegistry
from ._types.config_alias import ConfigAlias
from ._types.config_name import ConfigName
from ._types.config_specifier import ConfigSpecifier
from ._views.resolved_config import ResolvedConfig

__version__ = version("kiarina-utils-common")

__all__ = [
    "ConfigAlias",
    "ConfigName",
    "ConfigRegistry",
    "ConfigSpecifier",
    "ResolvedConfig",
]
