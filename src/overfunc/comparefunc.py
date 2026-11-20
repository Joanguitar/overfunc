from __future__ import annotations

from typing import Callable, Self

from overfunc.multifunc import MultiFunc, Register
from overfunc.typing import P, R, SupportsComparison
from overfunc.util import compose, get_self, attr_getter, flip_op


class CompareFuncRegister(Register[P, R]):
    def __init__(
        self,
        mfunc: CompareFunc[P, R],
        *validators: Callable[P, bool],
        priority: float | None = None,
    ) -> None:
        self.mfunc: CompareFunc[P, R]
        super().__init__(mfunc, *validators, priority=priority)

    def __op(
        self,
        op: Callable[[SupportsComparison], Callable[[SupportsComparison], bool]],
        **values: SupportsComparison,
    ) -> Self:
        new_validators = [
            compose(self.mfunc._getter(key), op(val)) for key, val in values.items()
        ]
        return self.__class__(self.mfunc, *self.validators, *new_validators)

    def __flop(
        self,
        op: Callable[[SupportsComparison], Callable[[SupportsComparison], bool]],
        **values: SupportsComparison,
    ) -> Self:
        return self.__op(flip_op(op), **values)

    def eq(self, **values: SupportsComparison) -> Self:
        return self.__flop(lambda actual: actual.__eq__, **values)

    def le(self, **values: SupportsComparison) -> Self:
        return self.__flop(lambda actual: actual.__le__, **values)

    def lt(self, **values: SupportsComparison) -> Self:
        return self.__flop(lambda actual: actual.__lt__, **values)

    def ge(self, **values: SupportsComparison) -> Self:
        return self.__flop(lambda actual: actual.__ge__, **values)

    def gt(self, **values: SupportsComparison) -> Self:
        return self.__flop(lambda actual: actual.__gt__, **values)


class CompareFunc(MultiFunc[P, R]):
    def __init__(
        self, func: Callable[P, R], **getters: Callable[P, SupportsComparison]
    ) -> None:
        super().__init__(func)
        self.__func = func
        self.__getters = getters

    def _getter(self, key: str) -> Callable[P, SupportsComparison]:
        return self.__getters[key]

    def with_getter(self, **getters: Callable[P, SupportsComparison]) -> Self:
        return self.__class__(self.__func, **self.__getters, **getters)

    def with_attr(self, **attr_names: str) -> Self:
        getters = {
            key: compose(get_self, attr_getter(attr_name))
            for key, attr_name in attr_names.items()
        }
        return self.__class__(self.__func, **self.__getters, **getters)

    def register(self, *validators: Callable[P, bool], priority: float | None = None):
        return CompareFuncRegister(self, *validators, priority=priority)
