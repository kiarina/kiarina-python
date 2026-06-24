from importlib.metadata import version

from ._services.component_registry import ComponentRegistry
from ._types.component_alias import ComponentAlias
from ._types.component_factory import ComponentFactory
from ._types.component_input import ComponentInput
from ._types.component_name import ComponentName
from ._types.component_specifier import ComponentSpecifier

__version__ = version("kiarina-utils-common")

__all__ = [
    "ComponentAlias",
    "ComponentFactory",
    "ComponentInput",
    "ComponentName",
    "ComponentRegistry",
    "ComponentSpecifier",
]
