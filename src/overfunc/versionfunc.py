from typing import Callable, Generic, Self

from overfunc.comparefunc import CompareFunc, CompareFuncRegister
from overfunc.typing import P, R, V, SupportsEqual


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

    def with_tag(self, **getters: Callable[P, SupportsEqual]):
        return self.__class__(self.__func, **self.__getters, **getters)  # type: ignore

    def register(self, *validators: Callable[P, bool], priority: float | None = None):
        return VersionFuncRegister(self, *validators, priority=priority)
