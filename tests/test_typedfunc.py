from __future__ import annotations

from typing import Any, Literal, Optional

import pytest

from overfunc.typedfunc import _matches_type, type_checker
from overfunc.typedfunc import TypedFunc
from overfunc.typing import MultiFuncError


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


def test_supports_any_none_union_literal_and_collection_annotations() -> None:
    def func(
        anything: Any,
        optional: Optional[int],
        mode: Literal["a", "b"],
        names: set[str],
        pair: tuple[int, str],
        repeated: tuple[int, ...],
    ) -> None:
        pass

    check = type_checker(func)

    assert check(object(), None, "a", {"x", "y"}, (1, "x"), (1, 2, 3))
    assert not check(object(), "one", "a", {"x"}, (1, "x"), (1, 2))  # type: ignore
    assert not check(object(), None, "c", {"x"}, (1, "x"), (1, 2))  # type: ignore
    assert not check(object(), None, "a", ["x"], (1, "x"), (1, 2))  # type: ignore
    assert not check(object(), None, "a", {"x"}, ("1", "x"), (1, 2))  # type: ignore
    assert not check(object(), None, "a", {"x"}, (1, "x"), (1, "two"))  # type: ignore


def test_supports_list_dict_tuple_and_unresolved_annotations() -> None:
    def func(
        values: list[int],
        mapping: dict[str, int],
        pair: tuple[int, str],
        unknown: object,
    ) -> None:
        pass

    check = type_checker(func)

    assert check([1, 2], {"a": 1}, (1, "x"), 42)
    assert not check([1, "x"], {"a": 1}, (1, "x"), 42)  # type: ignore
    assert not check([1], {1: "x"}, (1, "x"), 42)  # type: ignore
    assert not check([1], {"a": 1}, (1,), 42)  # type: ignore
    assert not check([1], {"a": 1}, (1, 2), 42)  # type: ignore


def test_typed_dispatch_and_additional_validators() -> None:
    @TypedFunc
    def convert(value: object) -> str: ...

    @convert.register(lambda value: value > 0)
    def positive_integer(value: int) -> str:
        return "positive"

    @convert.register()
    def text(value: str) -> str:
        return "text"

    assert convert(1) == "positive"
    assert convert("hello") == "text"
    with pytest.raises(MultiFuncError):
        convert(-1)
    with pytest.raises(MultiFuncError):
        convert(None)


def test_unannotated_parameters_are_not_checked() -> None:
    def func(value) -> None:
        pass

    check = type_checker(func)
    assert check(object())
    assert check(None)
    assert check(3)


def test_supported_internal_type_matches_cover_edge_cases() -> None:
    assert _matches_type([], list)
    assert _matches_type(set(), set)
    assert _matches_type({}, dict)
    assert _matches_type((1, 2), tuple)
    assert _matches_type(frozenset({1}), frozenset[int])
    assert _matches_type(None, None)
    assert not _matches_type(1, None)
    assert not _matches_type(1, 42)
    assert not _matches_type(1, list[int])
