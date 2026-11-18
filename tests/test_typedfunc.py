from overfunc.typedfunc import type_checker


def test_accepts_matching_argument_types() -> None:
    def func(count: int, label: str) -> None:
        pass

    check = type_checker(func)

    assert check(1, "item")
    assert check(count=1, label="item")


def test_rejects_mismatched_argument_types() -> None:
    def func(count: int, label: str) -> None:
        pass

    check = type_checker(func)

    assert not check("one", "item")  # type: ignore
    assert not check(1, label=2)  # type: ignore


def test_checks_types_in_variadic_arguments() -> None:
    def func(*values: int, **options: str) -> None:
        pass

    check = type_checker(func)

    assert check(1, 2, name="item")
    assert not check(1, "two")  # type: ignore
    assert not check(name=2)  # type: ignore


def test_checks_types_inside_list_and_dict_arguments() -> None:
    def func(values: list[int], options: dict[str, int]) -> None:
        pass

    check = type_checker(func)

    assert check([1, 2], {"count": 3})
    assert not check([1, "two"], {"count": 3})  # type: ignore
    assert not check([1], {"count": "three"})  # type: ignore


def test_rejects_calls_that_do_not_match_the_signature() -> None:
    def func(count: int) -> None:
        pass

    check = type_checker(func)

    assert not check()  # type: ignore
    assert not check(1, 2)  # type: ignore
