from __future__ import annotations

from typing import Callable, Generic

from overfunc.multifunc import MultiFunc
from overfunc.typing import P, R, RP, SupportsComparison


def compose(a: Callable[P, R], b: Callable[[R], RP]) -> Callable[P, RP]:
    def ab(*args: P.args, **kwargs: P.kwargs) -> RP:
        return b(a(*args, **kwargs))

    return ab


class CompareFuncRegister(Generic[P]):
    def __init__(
        self,
        cfunc: CompareFunc,
        *validators: Callable[P, bool],
        priority: float | None = None,
    ) -> None:
        self.__cfunc = cfunc
        self.__validators = validators
        self.__priority = priority

    def __op(
        self,
        op: Callable[[SupportsComparison], Callable[[SupportsComparison], bool]],
        **values: SupportsComparison,
    ):
        new_validators = [
            compose(self.__cfunc._getter(key), op(val)) for key, val in values.items()
        ]
        return CompareFuncRegister(self.__cfunc, *self.__validators, *new_validators)

    def eq(self, **values: SupportsComparison):
        return self.__op(
            lambda expected: lambda actual: actual.__eq__(expected), **values
        )

    def le(self, **values: SupportsComparison):
        return self.__op(
            lambda expected: lambda actual: actual.__le__(expected), **values
        )

    def lt(self, **values: SupportsComparison):
        return self.__op(
            lambda expected: lambda actual: actual.__lt__(expected), **values
        )

    def ge(self, **values: SupportsComparison):
        return self.__op(
            lambda expected: lambda actual: actual.__ge__(expected), **values
        )

    def gt(self, **values: SupportsComparison):
        return self.__op(
            lambda expected: lambda actual: actual.__gt__(expected), **values
        )

    def __call__(self, func: Callable[P, R]) -> Callable[P, R]:
        self.__cfunc._register(func, *self.__validators, priority=self.__priority)
        return func


class CompareFunc(MultiFunc[P, R]):
    def __init__(
        self, func: Callable[P, R], **getters: Callable[P, SupportsComparison]
    ) -> None:
        super().__init__(func)
        self.__func = func
        self.__getters = getters

    def _getter(self, key: str) -> Callable[P, SupportsComparison]:
        return self.__getters[key]

    def with_getters(
        self, **getters: Callable[P, SupportsComparison]
    ) -> CompareFunc[P, R]:
        return CompareFunc(self.__func, **self.__getters, **getters)

    def register(
        self,
        *validators: Callable[P, bool],
        priority: float | None = None,
    ) -> CompareFuncRegister[P]:
        return CompareFuncRegister(self, *validators, priority=priority)
