from functools import wraps
from types import MethodType
from typing import Callable, Generic, Iterable
from overfunc.typing import P, R, MultiFuncError


def _consolidate_validators(*validators: Callable[P, bool]) -> Callable[P, bool]:
    def validator(*args: P.args, **kwargs: P.kwargs) -> bool:
        return all(v(*args, **kwargs) for v in validators)

    return validator


class MultiFunc(Generic[P, R]):
    def __init__(
        self,
        func: Callable[P, R],
    ) -> None:
        self.__func = func
        self.__as_classmethod = isinstance(func, classmethod)
        self.__funcs_n: list[tuple[Callable[P, R], Callable[P, bool]]] = []
        self.__funcs_p: list[tuple[Callable[P, R], Callable[P, bool], float]] = []

    def __get__(self, instance: object | None, owner: type | None = None):
        if self.__as_classmethod:
            if owner is None:
                return self
            return MethodType(self, owner)
        if instance is None:
            return self
        return MethodType(self, instance)

    def _register(
        self,
        func: Callable[P, R],
        *validators: Callable[P, bool],
        priority: float | None = None,
    ) -> None:
        _func = wraps(self.__func)(func)
        validator = _consolidate_validators(*validators)
        if priority is None:
            self.__funcs_n.append((_func, validator))
        else:
            self.__funcs_p.append((_func, validator, priority))

    def register(
        self,
        *validators: Callable[P, bool],
        priority: float | None = None,
    ) -> Callable[[Callable[P, R]], Callable[P, R]]:
        def wrapper(func: Callable[P, R]) -> Callable[P, R]:
            self._register(func, *validators, priority=priority)
            return func

        return wrapper

    @property
    def __func_vals(self) -> Iterable[tuple[Callable[P, R], Callable[P, bool]]]:
        self.__funcs_p.sort(key=lambda v: v[-1], reverse=True)
        for _func, _val, _ in self.__funcs_p:
            yield _func, _val
        for _func, _val in self.__funcs_n:
            yield _func, _val

    def __call__(self, *args, **kwargs) -> R:
        for func, val in self.__func_vals:
            if val(*args, **kwargs):
                return func(*args, **kwargs)
        raise MultiFuncError(
            f"Couldn't find implementation for {self.__func.__name__}."
        )
