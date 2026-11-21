from overfunc.util import attr_getter, compose, flip_op, get_self


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
    flipped_greater_than = flip_op(lambda actual: actual.__gt__)
    assert flipped_greater_than(10)(20)
