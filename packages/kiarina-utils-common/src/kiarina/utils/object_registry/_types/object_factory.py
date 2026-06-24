from typing import Protocol, TypeVar

from .object_name import ObjectName

TObject_co = TypeVar("TObject_co", covariant=True)
TConfig_contra = TypeVar("TConfig_contra", contravariant=True)


class ObjectFactory(Protocol[TObject_co, TConfig_contra]):
    def __call__(
        self, object_name: ObjectName, config: TConfig_contra, /
    ) -> TObject_co: ...
