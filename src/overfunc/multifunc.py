"""Register and dispatch function implementations using validation predicates."""

from __future__ import annotations

from functools import wraps
from types import MethodType
from typing import Callable, Generic, Iterable, Self, final
from overfunc.typing import P, R, MultiFuncError


def _consolidate_validators(*validators: Callable[P, bool]) -> Callable[P, bool]:
    """Combine validators so the returned predicate requires all of them."""

    def validator(*args: P.args, **kwargs: P.kwargs) -> bool:
        """Return whether every constituent validator accepts the call."""
        return all(v(*args, **kwargs) for v in validators)

    return validator


class Register(Generic[P, R]):
    """Configure and apply a registration to a multi-function dispatcher."""

    def __init__(
        self,
        mfunc: MultiFunc[P, R],
        *validators: Callable[P, bool],
        priority: float | None = None,
    ):
        """Store the dispatcher and rules for the implementation being registered."""
        self.mfunc = mfunc
        self.validators = validators
        self.priority = priority

    def __call__(self, func: Callable[P, R]) -> Callable[P, R]:
        """Register the decorated function and return it unchanged."""
        self.mfunc._register(func, *self.validators, priority=self.priority)
        return func

    def with_validator(self, *validators: Callable[P, bool]):
        """Return a registration builder with additional validators."""
        return self.__class__(
            self.mfunc, *self.validators, *validators, priority=self.priority
        )

    def with_priority(self, priority: float | None = None):
        """Return a registration builder configured with the given priority."""
        return self.__class__(self.mfunc, *self.validators, priority=priority)


class MultiFunc(Generic[P, R]):
    """Dispatch calls to the first registered implementation whose validators pass."""

    def __init__(
        self,
        func: Callable[P, R],
    ) -> None:
        """Initialize the dispatcher with its wrapped function and empty registry."""
        self.__func = func
        self.__as_classmethod = isinstance(func, classmethod)
        self.__funcs_n: list[tuple[Callable[P, R], Callable[P, bool]]] = []
        self.__funcs_p: list[tuple[Callable[P, R], Callable[P, bool], float]] = []

    def _clone(self) -> Self:
        """Clone the dispatcher while sharing its registered implementation lists."""
        new = self.__class__(self.__func)
        new.__funcs_n = self.__funcs_n
        new.__funcs_p = self.__funcs_p
        return new

    @final
    def __get__(self, instance: object | None, owner: type | None = None):
        """Bind the dispatcher as a method when accessed through an instance."""
        if self.__as_classmethod:
            if owner is None:
                return self
            return MethodType(self, owner)
        if instance is None:
            return self
        return MethodType(self, instance)

    def _wraps(self, func: Callable[P, R]):
        """Apply the wrapped function's metadata to a registered implementation."""
        return wraps(self.__func)(func)

    @final
    def _register(
        self,
        func: Callable[P, R],
        *validators: Callable[P, bool],
        priority: float | None = None,
    ) -> None:
        """Add an implementation and its combined validator to the registry."""
        _func = self._wraps(func)
        validator = _consolidate_validators(*validators)
        if priority is None:
            self.__funcs_n.append((_func, validator))
        else:
            self.__funcs_p.append((_func, validator, priority))

    def register(
        self,
        *validators: Callable[P, bool],
        priority: float | None = None,
    ):
        """Create a builder for registering an implementation."""
        return Register(self, *validators, priority=priority)

    @final
    @property
    def __func_vals(self) -> Iterable[tuple[Callable[P, R], Callable[P, bool]]]:
        """Yield prioritized registrations before registrations without a priority."""
        self.__funcs_p.sort(key=lambda v: v[-1], reverse=True)
        for _func, _val, _ in self.__funcs_p:
            yield _func, _val
        for _func, _val in self.__funcs_n:
            yield _func, _val

    @final
    def __call__(self, *args, **kwargs) -> R:
        """Call the first implementation whose validators accept the arguments."""
        for func, val in self.__func_vals:
            if val(*args, **kwargs):
                return func(*args, **kwargs)
        raise MultiFuncError(
            f"Couldn't find implementation for {self.__func.__name__}."
        )
