import pytest

from overfunc.versionfunc import VersionedDecorator


class Instrument:
    """Instrument with buggy implementation for different versions."""

    def __init__(self, name: str, version: int) -> None:
        self.name = name
        self.version = version

        self.a = 0
        self.b = 0
        self.c = 0

    @property
    def starting_str(self) -> str:
        if self.version < 4:
            return f"{self.name}({self.version}):"
        return f"{self.name}[{self.version}]:"  # Version 4 changed style

    def communicate(self, query: str):
        assert query.startswith(self.starting_str)
        query = query.lstrip(self.starting_str)
        key, val_str = query.split("=")
        val = int(val_str)
        if key == "a":
            self.a = val
            if self.name.startswith("Buggy") and self.version < 2:
                # Buggy before version 2
                self.b = val
        elif key == "b":
            if self.version < 3:
                # Versions prior to 3 save b in c
                self.c = val
            else:
                self.b = val
        else:
            raise KeyError("Wrong attr name", key)


class ClassWithInstrument:
    def __init__(self, instrument: Instrument) -> None:
        self.instrument = instrument

    @property
    def instrument_name(self) -> str:
        return self.instrument.name

    @property
    def instrument_version(self) -> int:
        return self.instrument.version

    instrument_decorator = (
        VersionedDecorator()
        .with_version_from_attr("instrument_version")
        .with_tag_from_attr("instrument_name")
    )

    @instrument_decorator
    def get_instrument_starting_str(self) -> str: ...

    instrument_starting_str = property(get_instrument_starting_str)

    @get_instrument_starting_str.register().for_version(final=4)
    def _(self) -> str:  # Implementation with parenthesis (version < 4)
        return f"{self.instrument.name}({self.instrument.version}):"

    @get_instrument_starting_str.register().for_version(initial=4)
    def _(self) -> str:  # Implementation with brakets (version >= 4)
        return f"{self.instrument.name}[{self.instrument.version}]:"

    def get_a(self) -> int:
        return self.instrument.a

    @instrument_decorator
    def get_b(self) -> int: ...

    @get_b.register().for_version(final=3)
    def _(self) -> int:  # Bug workaround (saving to c)
        return self.instrument.c

    @get_b.register().for_version(initial=3)
    def _(self) -> int:  # After bugfix implementation
        return self.instrument.b

    @instrument_decorator
    def set_a(self, a: int) -> None: ...

    @set_a.register()
    def _(self, a: int) -> None:  # Default not-buggy
        self.instrument.communicate(f"{self.instrument_starting_str}a={a}")

    @(
        set_a.register(priority=1)
        .for_tag(instrument_name="BuggyInstrument")
        .for_version(final=2)
    )
    def _(self, a: int) -> None:  # Overriding b workaround
        b = self.get_b()
        self.instrument.communicate(f"{self.instrument_starting_str}a={a}")
        self.set_b(b)

    def set_b(self, b: int) -> None:
        self.instrument.communicate(f"{self.instrument_starting_str}b={b}")

    def set_ab(self, a: int, b: int) -> None:
        self.set_b(b)
        self.set_a(a)

    def get_ab(self) -> tuple[int, int]:
        return self.get_a(), self.get_b()


@pytest.mark.parametrize("name", ["NotTooBuggyInstrument", "BuggyInstrument"])
@pytest.mark.parametrize("version", [1, 2, 3, 4])
def test_ab(name: str, version: int):
    instrument = Instrument(name, version)
    instance = ClassWithInstrument(instrument)

    for a in (-1, 0, 1):
        for b in (-1, 0, 1):
            instance.set_ab(a, b)
            assert instance.get_ab() == (a, b)

    for b in (-1, 0, 1):
        instance.set_b(b)
        for a in (-1, 0, 1):
            instance.set_a(a)
            assert instance.get_ab() == (a, b)
