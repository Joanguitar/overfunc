"""Small callable composition and attribute-access helpers."""

from typing import Callable

from overfunc.typing import P, R, RP, S, T1, T2


def compose(a: Callable[P, R], b: Callable[[R], RP]) -> Callable[P, RP]:
    """Return a callable that applies ``a`` and then ``b``."""

    def ab(*args: P.args, **kwargs: P.kwargs) -> RP:
        """Apply the composed functions to the supplied arguments."""
        return b(a(*args, **kwargs))

    return ab


def get_self(self: S, *args, **kwargs) -> S:
    """Return the first argument, ignoring any additional arguments."""
    return self


def attr_getter(name: str):
    """Create a callable that retrieves the named attribute from its first argument."""

    def getter(self: object):
        """Return the named attribute from the supplied object."""
        return getattr(self, name)

    return getter


def flip_op(op: Callable[[T1], Callable[[T2], R]]) -> Callable[[T2], Callable[[T1], R]]:
    """Return an operator wrapper that reverses the order of its two operands."""

    def flop(b: T2) -> Callable[[T1], R]:
        """Bind the second operand and return a callable for the first."""

        def _op(a: T1) -> R:
            """Apply the original operator to the operands in reversed order."""
            return op(a)(b)

        return _op

    return flop
