"""Dispatch functions based on comparisons of values extracted from arguments."""

from __future__ import annotations

from typing import Callable, Generic, Self

from overfunc.multifunc import MultiFunc, Register
from overfunc.typing import P, R, SupportsComparison
from overfunc.util import compose, get_self, attr_getter, flip_op


class CompareFuncRegister(Register[P, R]):
    """Build comparison predicates for a registered implementation."""

    def __init__(
        self,
        mfunc: CompareFunc[P, R],
        *validators: Callable[P, bool],
        priority: float | None = None,
    ) -> None:
        """Create a registration builder for a comparison dispatcher."""
        self.mfunc: CompareFunc[P, R]
        super().__init__(mfunc, *validators, priority=priority)

    def __op(
        self,
        op: Callable[[SupportsComparison], Callable[[SupportsComparison], bool]],
        **values: SupportsComparison,
    ) -> Self:
        """Add comparison validators for the configured getter values."""
        new_validators = [
            compose(self.mfunc._getters[key], op(val)) for key, val in values.items()
        ]
        return self.__class__(self.mfunc, *self.validators, *new_validators)

    def __flop(
        self,
        op: Callable[[SupportsComparison], Callable[[SupportsComparison], bool]],
        **values: SupportsComparison,
    ) -> Self:
        """Add validators using the comparison operator with operands flipped."""
        return self.__op(flip_op(op), **values)

    def eq(self, **values: SupportsComparison) -> Self:
        """Require getter values to equal the supplied values."""
        return self.__flop(lambda actual: actual.__eq__, **values)

    def le(self, **values: SupportsComparison) -> Self:
        """Require getter values to be less than or equal to the supplied values."""
        return self.__flop(lambda actual: actual.__le__, **values)

    def lt(self, **values: SupportsComparison) -> Self:
        """Require getter values to be less than the supplied values."""
        return self.__flop(lambda actual: actual.__lt__, **values)

    def ge(self, **values: SupportsComparison) -> Self:
        """Require getter values to be greater than or equal to the supplied values."""
        return self.__flop(lambda actual: actual.__ge__, **values)

    def gt(self, **values: SupportsComparison) -> Self:
        """Require getter values to be greater than the supplied values."""
        return self.__flop(lambda actual: actual.__gt__, **values)


class CompareDecorator(Generic[P]):
    """Configure getters for comparison-based function dispatch."""

    def __init__(self, **getters: Callable[P, SupportsComparison]) -> None:
        """Initialize the getter functions used by comparison rules."""
        super().__init__()
        self._getters = getters

    def _clone(self, getters: dict[str, Callable[P, SupportsComparison]]):
        """Create a new decorator configured with the supplied getters."""
        return self.__class__(**getters)

    def with_getter(self, **getters: Callable[P, SupportsComparison]) -> Self:
        """Return a clone with the given getter functions added or replaced."""
        return self._clone(getters={**self._getters, **getters})

    def with_attr(self, **attr_names: str) -> Self:
        """Return a clone with getters that read named attributes from arguments."""
        getters = {
            key: compose(get_self, attr_getter(attr_name))
            for key, attr_name in attr_names.items()
        }
        return self.with_getter(**getters)

    def __call__(self, func: Callable[P, R]):
        """Wrap a function in a comparison dispatcher using the configured getters."""
        return CompareFunc(func, **self._getters)


class CompareFunc(MultiFunc[P, R], CompareDecorator[P]):
    """Dispatch implementations according to comparisons of extracted values."""

    def __init__(
        self, func: Callable[P, R], **getters: Callable[P, SupportsComparison]
    ) -> None:
        """Initialize a dispatcher with its default function and value getters."""
        super().__init__(func)
        self._getters = getters

    def _clone(
        self, getters: None | dict[str, Callable[P, SupportsComparison]] = None
    ) -> Self:
        """Clone the dispatcher, sharing registered implementations."""
        new = super()._clone()
        if getters is None:
            new._getters = self._getters.copy()
        else:
            new._getters = getters
        return new

    def register(self, *validators: Callable[P, bool], priority: float | None = None):
        """Create a builder for a comparison- and predicate-guarded implementation."""
        return CompareFuncRegister(self, *validators, priority=priority)
