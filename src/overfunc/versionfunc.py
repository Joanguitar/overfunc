from typing import Callable, Generic, Self

from overfunc.comparefunc import CompareFunc, CompareFuncRegister, CompareDecorator
from overfunc.typing import P, R, V, SupportsEqual
from overfunc.util import compose, get_self, attr_getter


class VersionFuncRegister(CompareFuncRegister[P, R], Generic[P, R, V]):
    def for_version(self, initial: V | None = None, final: V | None = None) -> Self:
        new = self
        if initial is not None:
            new = new.ge(version=initial)
        if final is not None:
            new = new.lt(version=final)
        return new

    def for_tag(self, **tags):
        return self.eq(**tags)


class VersionDecorator(CompareDecorator[P], Generic[P, V]):
    def __init__(
        self,
        version: Callable[P, V] | None = None,
        **getters: Callable[P, SupportsEqual],
    ) -> None:
        if version is None:
            super().__init__(func, **getters)  # type: ignore
        else:
            super().__init__(func, version=version, **getters)  # type: ignore

    def with_version_getter(self, getter: Callable[P, V]):
        return self.with_getter(version=getter)

    def with_version_from_attr(self, attr_name: str):
        self.with_version_getter(compose(get_self, attr_getter(attr_name)))

    def with_tag_getter(self, **getters: Callable[P, SupportsEqual]):
        self.with_getter(*getters)

    def with_tag_from_attr(self, *tag: str):
        return self.with_attr(*tag)

class VersionFunc(CompareFunc[P, R], VersionDecorator[P, V], Generic[P, R, V]):
    def __init__(
        self,
        func: Callable[P, R],
        version: Callable[P, V] | None = None,
        **getters: Callable[P, SupportsEqual],
    ) -> None:
        if version is None:
            super().__init__(func, **getters)  # type: ignore
        else:
            super().__init__(func, version=version, **getters)  # type: ignore

    def register(self, *validators: Callable[P, bool], priority: float | None = None):
        return VersionFuncRegister(self, *validators, priority=priority)
