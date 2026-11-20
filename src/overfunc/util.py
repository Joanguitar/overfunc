from typing import Callable

from overfunc.typing import P, R, RP, S, T1, T2


def compose(a: Callable[P, R], b: Callable[[R], RP]) -> Callable[P, RP]:
    def ab(*args: P.args, **kwargs: P.kwargs) -> RP:
        return b(a(*args, **kwargs))

    return ab


def get_self(self: S, *args, **kwargs) -> S:
    return self


def attr_getter(name: str):
    def getter(self: object):
        return getattr(self, name)

    return getter


def flip_op(op: Callable[[T1], Callable[[T2], R]]) -> Callable[[T2], Callable[[T1], R]]:
    def flop(b: T2) -> Callable[[T1], R]:
        def _op(a: T1) -> R:
            return op(a)(b)

        return _op

    return flop
