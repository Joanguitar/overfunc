import pytest

from overfunc.comparefunc import CompareDecorator, CompareFunc
from overfunc.typing import MultiFuncError


def test_dispatches_with_comparison_conditions() -> None:
    @CompareDecorator(value=lambda value: value)
    def choose(value: int) -> str: ...

    @choose.register().ge(value=12).lt(value=20)
    def in_range(value: int) -> str:
        return "range"

    @choose.register().gt(value=20)
    def greater_than_twenty(value: int) -> str:
        return "greater"

    @choose.register().ge(value=10)
    def at_least_ten(value: int) -> str:
        return "at least ten"

    @choose.register().eq(value=5)
    def equal_to_five(value: int) -> str:
        return "equal"

    @choose.register().lt(value=0)
    def below_zero(value: int) -> str:
        return "negative"

    @choose.register().le(value=3)
    def at_most_three(value: int) -> str:
        return "at most three"

    @choose.register(lambda value: value % 2 == 0).eq(value=8)
    def even_eight(value: int) -> str:
        return "even eight"

    @choose.register()
    def fallback(value: int) -> str:
        return "other"

    assert choose(15) == "range"
    assert choose(21) == "greater"
    assert choose(10) == "at least ten"
    assert choose(5) == "equal"
    assert choose(3) == "at most three"
    assert choose(-1) == "negative"
    assert choose(8) == "even eight"
    assert choose(7) == "other"


def test_with_getters_adds_another_comparison_field() -> None:
    @CompareDecorator(value=lambda value: value).with_getter(
        first_letter=lambda value: value[0]
    )
    def choose(value: str) -> str: ...

    @choose.register().eq(first_letter="a")
    def starts_with_a(value: str) -> str:
        return "a"

    assert choose("apple") == "a"


def test_with_attr_reads_attributes_for_comparison() -> None:
    class Number:
        def __init__(self, value: int) -> None:
            self.value = value

    @CompareDecorator().with_attr("value")
    def choose(number: Number) -> str: ...

    @choose.register().ge(value=10)
    def ten_or_more(number: Number) -> str:
        return "ten or more"

    assert choose(Number(10)) == "ten or more"


def test_clone_can_replace_getters() -> None:
    @CompareDecorator(original=lambda value: value)
    def choose(value: int) -> str: ...

    clone = choose._clone({"replacement": lambda value: value})

    @clone.register().eq(replacement=3)
    def three(value: int) -> str:
        return "three"

    assert clone(3) == "three"


def test_clone_without_getters_keeps_existing_getters() -> None:
    @CompareDecorator(value=lambda value: value)
    def choose(value: int) -> str: ...

    clone = choose._clone()

    @clone.register().eq(value=4)
    def four(value: int) -> str:
        return "four"

    assert clone(4) == "four"


def test_compare_decorator_builds_a_dispatcher() -> None:
    @CompareDecorator(value=lambda value: value)
    def dispatcher(value: int) -> str: ...

    @dispatcher.register().eq(value=2)
    def two(value: int) -> str:
        return "two"

    assert isinstance(dispatcher, CompareFunc)
    assert dispatcher(2) == "two"

def test_decorator() -> None:
    class Number:
        def __init__(self, value: int) -> None:
            self.value = value

        ValueDecorator = CompareDecorator().with_attr("value")

        @ValueDecorator
        def what_am_i(self) -> str: ...

        @what_am_i.register().lt(value=0)
        def _(self) -> str:
            return f"{self.value} is negative"

        @what_am_i.register(priority=100).gt(value=100)
        def _(self) -> str:
            return "Quite big"

        @what_am_i.register(priority=3).ge(value=0).lt(value=10)
        def _(self) -> str:
            return "One digit long"

        @what_am_i.register(priority=10).ge(value=9).lt(value=100)
        def _(self) -> str:
            return "Two digits long"

    for ii in (1, 5, 9):
        assert Number(ii).what_am_i() == "One digit long"
    for ii in (11, 15, 91):
        assert Number(ii).what_am_i() == "Two digits long"
    for ii in (-1, -100, -10000):
        assert Number(ii).what_am_i() == f"{ii} is negative"
    for ii in (1000, 10000):
        assert Number(ii).what_am_i() == "Quite big"
    with pytest.raises(MultiFuncError):
        Number(100).what_am_i()
