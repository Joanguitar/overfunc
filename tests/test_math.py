from contextlib import contextmanager
import sys

from overfunc.multifunc import MultiFunc
from overfunc.typedfunc import TypedFunc


@contextmanager
def increase_rec_lim(rec_lim: int):
    original = sys.getrecursionlimit()
    try:
        yield sys.setrecursionlimit(rec_lim)
    finally:
        sys.setrecursionlimit(original)


# Collatz


def is_odd(number: int) -> bool:
    return bool(number % 2)


def is_even(number: int) -> bool:
    return not number % 2


@MultiFunc
def collatz(number: int) -> int: ...


@collatz.register(is_even)
def _(number: int) -> int:
    next_number = number // 2
    if next_number == 1:
        return 1
    return 1 + collatz(next_number)


@collatz.register(is_odd)
def _(number: int) -> int:
    if number == 1:
        return 0
    return 1 + collatz(3 * number + 1)


def test_collatz():
    with increase_rec_lim(10**6):
        for ii, c in enumerate([0, 1, 7, 2, 5, 8, 16, 3, 19, 6, 14, 9], start=1):
            assert collatz(ii) == c


# Modulo 9


@TypedFunc
def mod9(number: int | str) -> int: ...


@mod9.register()
def _(number: int) -> int:
    if number < 0:
        return mod9(9 - mod9(str(-number)))
    if number > 9:
        return mod9(str(number))
    if number == 9:
        return 0
    return number


@mod9.register()
def _(number: str) -> int:
    return mod9(sum(int(d) for d in number))


def test_mod9():
    for ii in range(-10, 20):
        assert mod9(ii) == ii % 9


# Modulo 11


@TypedFunc
def mod11(number: int | str | tuple[int, ...]) -> int: ...


@mod11.register()
def _(number: int) -> int:
    if number < 0:
        return mod11(11 - mod11(-number))
    if number > 10:
        return mod11(str(number))
    return number


@mod11.register()
def _(number: tuple[int, ...]) -> int:
    dp = sum(d for d in number[-1::-2])
    dn = sum(d for d in number[-2::-2])
    return mod11(dp - dn)


@mod11.register()
def _(number: str) -> int:
    return mod11(tuple(int(d) for d in number))


def test_mod11():
    for ii in [-20, 200, 1351, 1564897]:
        val = ii % 11
        assert mod11(ii) == ii % 11
