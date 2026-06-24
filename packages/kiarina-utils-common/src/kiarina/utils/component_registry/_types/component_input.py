from typing import TypeAlias, TypeVar

from .component_specifier import ComponentSpecifier

T = TypeVar("T")

ComponentInput: TypeAlias = T | ComponentSpecifier
