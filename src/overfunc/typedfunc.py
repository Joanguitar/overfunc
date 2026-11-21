"""Dispatch function implementations according to their argument type hints."""

from inspect import signature
from typing import Any, Callable, Literal, Union, get_args, get_origin, get_type_hints

from overfunc.multifunc import MultiFunc, Register
from overfunc.typing import P, R


def type_checker(func: Callable[P, R]) -> Callable[P, bool]:
    """Build a predicate that checks calls against a function's parameter hints."""
    _sig = signature(func)
    _hints = get_type_hints(func)

    def validator(*args: P.args, **kwargs: P.kwargs) -> bool:
        """Return whether the arguments bind and satisfy the annotated types."""
        try:
            bound = _sig.bind(*args, **kwargs)
        except (TypeError, ValueError):
            return False

        for name, value in bound.arguments.items():
            parameter = _sig.parameters[name]
            annotation = _hints.get(name, parameter.annotation)
            if annotation is parameter.empty:
                continue
            if parameter.kind is parameter.VAR_POSITIONAL:
                if not all(_matches_type(item, annotation) for item in value):
                    return False
            elif parameter.kind is parameter.VAR_KEYWORD:
                if not all(_matches_type(item, annotation) for item in value.values()):
                    return False
            elif not _matches_type(value, annotation):
                return False
        return True

    return validator


def _matches_type(value: object, annotation: object) -> bool:
    """Check a value against supported runtime typing annotations."""
    if annotation is Any:
        return True

    origin = get_origin(annotation)
    types = get_args(annotation)

    if origin is Union or getattr(origin, "__name__", "") == "UnionType":
        return any(_matches_type(value, item) for item in types)
    if origin is Literal:
        return any(type(value) is type(item) and value == item for item in types)
    if origin is not None:
        if not isinstance(value, origin):
            return False
        if origin is list or origin is set:
            if not isinstance(value, (list, set)):
                return False
            return not types or all(_matches_type(item, types[0]) for item in value)
        if origin is dict:
            if not isinstance(value, dict):
                return False
            return not types or all(
                _matches_type(key, types[0]) and _matches_type(item, types[1])
                for key, item in value.items()
            )
        if origin is tuple and types:
            if not isinstance(value, tuple):
                return False
            if len(types) == 2 and types[1] is Ellipsis:
                return all(_matches_type(item, types[0]) for item in value)
            return len(value) == len(types) and all(
                _matches_type(item, item_type) for item, item_type in zip(value, types)
            )
        return True

    if annotation is None:
        return value is None
    try:
        return isinstance(value, annotation)  # type: ignore
    except TypeError:
        return False


class TypedFuncRegister(Register):
    """Register functions with an argument-type check preceding other validators."""

    def __call__(self, func: Callable[P, R]) -> Callable[P, R]:
        """Register the function with its inferred type checker."""
        self.mfunc._register(
            func, type_checker(func), *self.validators, priority=self.priority
        )
        return func


class TypedFunc(MultiFunc[P, R]):
    """Dispatch calls to implementations whose annotated argument types match."""

    def register(self, *validators: Callable[P, bool], priority: float | None = None):
        """Create a registration builder that checks the function's type hints."""
        return TypedFuncRegister(self, *validators, priority=priority)
