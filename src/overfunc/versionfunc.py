from typing import Callable, Generic, Self

from overfunc.comparefunc import CompareFunc, CompareFuncRegister
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


class VersionFunc(CompareFunc[P, R], Generic[P, R, V]):
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

    def with_version_getter(self, getter: Callable[P, V]):
        return self.__class__(self.__func, **self.__getters, version=getter)

    def with_version_from_attr(self, attr_name: str):
        self.with_version_getter(compose(get_self, attr_getter(attr_name)))

    def with_tag_getter(self, **getters: Callable[P, SupportsEqual]):
        self.with_getter(*getters)

    def with_tag_from_attr(self, *tag: str):
        return self.with_attr(*tag)

    def register(self, *validators: Callable[P, bool], priority: float | None = None):
        return VersionFuncRegister(self, *validators, priority=priority)
