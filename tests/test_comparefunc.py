from overfunc.comparefunc import CompareFunc


def test_dispatches_with_comparison_conditions() -> None:
    def choose(value: int) -> str:
        raise NotImplementedError

    compare = CompareFunc(choose, value=lambda value: value)

    @compare.register().ge(value=12).lt(value=20)
    def in_range(value: int) -> str:
        return "range"

    @compare.register().gt(value=20)
    def greater_than_twenty(value: int) -> str:
        return "greater"

    @compare.register().ge(value=10)
    def at_least_ten(value: int) -> str:
        return "at least ten"

    @compare.register().eq(value=5)
    def equal_to_five(value: int) -> str:
        return "equal"

    @compare.register().lt(value=0)
    def below_zero(value: int) -> str:
        return "negative"

    @compare.register().le(value=3)
    def at_most_three(value: int) -> str:
        return "at most three"

    @compare.register(lambda value: value % 2 == 0).eq(value=8)
    def even_eight(value: int) -> str:
        return "even eight"

    @compare.register()
    def fallback(value: int) -> str:
        return "other"

    assert compare(15) == "range"
    assert compare(21) == "greater"
    assert compare(10) == "at least ten"
    assert compare(5) == "equal"
    assert compare(3) == "at most three"
    assert compare(-1) == "negative"
    assert compare(8) == "even eight"
    assert compare(7) == "other"


def test_with_getters_adds_another_comparison_field() -> None:
    def choose(value: str) -> str:
        raise NotImplementedError

    compare = CompareFunc(choose, value=lambda value: value)
    compare = compare.with_getter(first_letter=lambda value: value[0])

    @compare.register().eq(first_letter="a")
    def starts_with_a(value: str) -> str:
        return "a"

    assert compare("apple") == "a"
