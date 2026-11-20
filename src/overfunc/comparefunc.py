from __future__ import annotations

from typing import Callable, Generic, Self

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
            compose(self.mfunc._getters[key], op(val)) for key, val in values.items()
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

class CompareDecorator(Generic[P]):
    def __init__(
        self, **getters: Callable[P, SupportsComparison]
    ) -> None:
        super().__init__()
        self._getters = getters

    def _clone(self, getters: dict[str, Callable[P, SupportsComparison]]):
        return self.__class__(**getters)

    def with_getter(self, **getters: Callable[P, SupportsComparison]) -> Self:
        return self._clone(getters = {**self._getters, **getters})

    def with_attr(self, **attr_names: str) -> Self:
        getters = {
            key: compose(get_self, attr_getter(attr_name))
            for key, attr_name in attr_names.items()
        }
        return self.with_getter(**getters)


class CompareFunc(MultiFunc[P, R], CompareDecorator[P]):
    def __init__(
        self, func: Callable[P, R], **getters: Callable[P, SupportsComparison]
    ) -> None:
        super().__init__(func)
        self._getters = getters

    def _clone(self, getters: None | dict[str, Callable[P, SupportsComparison]] = None) -> Self:
        new = super()._clone()
        if getters is None:
            new._getters = self._getters.copy()
        else:
            new._getters = getters
        return new

    def register(self, *validators: Callable[P, bool], priority: float | None = None):
        return CompareFuncRegister(self, *validators, priority=priority)
