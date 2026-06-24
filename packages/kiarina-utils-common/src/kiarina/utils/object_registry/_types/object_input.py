from typing import TypeAlias, TypeVar

from .object_specifier import ObjectSpecifier

TObject = TypeVar("TObject")

ObjectInput: TypeAlias = TObject | ObjectSpecifier
