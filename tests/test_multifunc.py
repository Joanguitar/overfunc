import pytest

from overfunc.multifunc import MultiFunc
from overfunc.typing import MultiFuncError


def test_registers_validators_with_priority_and_fallback() -> None:
    @MultiFunc
    def describe(value: int) -> str: ...

    @describe.register(lambda value: value >= 0)
    def first(value: int) -> str:
        return "first"

    @describe.register(
        lambda value: value >= 0,
        lambda value: value == 10,
        priority=20,
    )
    def priority(value: int) -> str:
        return "priority"

    @describe.register()
    def fallback(value: int) -> str:
        return "fallback"

    assert describe(10) == "priority"
    assert describe(1) == "first"
    assert describe(-1) == "fallback"


def test_registration_builder_adds_validators_and_priority() -> None:
    @MultiFunc
    def classify(value: int) -> str: ...

    builder = (
        classify.register().with_validator(lambda value: value > 0).with_priority(5)
    )

    @builder
    def positive(value: int) -> str:
        return "positive"

    assert classify(3) == "positive"
    with pytest.raises(MultiFuncError):
        classify(-1)


def test_clone_shares_registrations() -> None:
    @MultiFunc
    def choose(value: int) -> str: ...

    @choose.register(lambda value: value == 1)
    def one(value: int) -> str:
        return "one"

    cloned = choose._clone()
    assert cloned(1) == "one"


def test_dispatches_instance_methods() -> None:
    class Example:
        @MultiFunc
        def choose(self, value: int) -> str: ...

        @choose.register(lambda self, value: value > 0)
        def positive(self, value: int) -> str:
            return "positive"

    assert Example().choose(1) == "positive"


def test_dispatches_class_methods() -> None:
    class Example:
        @MultiFunc
        @classmethod
        def choose(cls, value: int) -> str: ...

        @choose.register(lambda cls, value: value > 0)
        @classmethod
        def positive(cls, value: int) -> str:
            return "positive"

    assert Example.choose(1) == "positive"


def test_preserves_dispatcher_metadata_on_implementations() -> None:
    @MultiFunc
    def choose(value: int) -> str:
        """Choose an implementation."""
        raise NotImplementedError

    @choose.register()
    def implementation(value: int) -> str:
        """Implementation documentation."""
        return "chosen"

    assert implementation.__name__ == "choose"
    assert implementation.__doc__ == "Choose an implementation."
    assert choose(1) == "chosen"
