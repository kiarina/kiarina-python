from importlib.metadata import version

from ._services.object_registry import ObjectRegistry
from ._types.object_alias import ObjectAlias
from ._types.object_factory import ObjectFactory
from ._types.object_input import ObjectInput
from ._types.object_name import ObjectName
from ._types.object_specifier import ObjectSpecifier

__version__ = version("kiarina-utils-common")

__all__ = [
    "ObjectAlias",
    "ObjectFactory",
    "ObjectInput",
    "ObjectName",
    "ObjectRegistry",
    "ObjectSpecifier",
]
