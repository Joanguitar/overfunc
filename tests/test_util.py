from overfunc.util import attr_getter, compose, flip_op, get_self
from overfunc.typing import SupportsComparison


def test_compose_applies_functions_in_order() -> None:
    assert compose(lambda value: value * 2, str)(3) == "6"


def test_get_self_ignores_extra_arguments() -> None:
    value = object()
    assert get_self(value, 1, key="value") is value


def test_attr_getter_reads_named_attributes() -> None:
    class Example:
        name = "item"

    assert attr_getter("name")(Example()) == "item"


def test_flip_op_reverses_operand_order() -> None:
    def gt(actual: SupportsComparison):
        return actual.__gt__

    flipped_gt = flip_op(gt)
    for a, b in [(10, 20), (1, 2), ("a", "b"), (-5.1, 1.2), ("one", "one")]:
        _gt = gt(a)(b)
        assert isinstance(_gt, bool)
        assert _gt == flipped_gt(b)(a)
