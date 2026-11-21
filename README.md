# overfunc

`overfunc` dispatches a call to one of several registered implementations.
Use `MultiFunc` with explicit validators, `TypedFunc` with argument
annotations, or comparison and version decorators for common dispatch rules.

## Installation

```bash
pip install overfunc
```

Python 3.9 or newer is required.

## MultiFunc

Create a dispatcher with a representative function, then register
implementations with validators. Validators receive the same arguments as the
call and return `True` when their implementation should be selected.

```python
from overfunc import MultiFunc


@MultiFunc
def describe(value: object) -> str:
    raise NotImplementedError


@describe.register(lambda value: isinstance(value, int))
def describe_integer(value: object) -> str:
    return f"integer: {value}"


@describe.register(lambda value: isinstance(value, str))
def describe_string(value: object) -> str:
    return f"string: {value}"


print(describe(42))       # integer: 42
print(describe("hello"))  # string: hello
```

When multiple validators match, implementations registered with a priority
are checked first, from highest to lowest. Implementations without a priority
are checked afterward in registration order.

```python
@describe.register(
    lambda value: isinstance(value, int) and value > 0,
    priority=10,
)
def describe_positive_integer(value: object) -> str:
    return f"positive integer: {value}"
```

If no validator matches, the dispatcher raises `MultiFuncError`.

## TypedFunc

`TypedFunc` adds a validator that checks whether the call fits the registered
implementation's signature and whether annotated arguments match their types.
Arguments without annotations are not type-checked.

```python
from overfunc import TypedFunc


@TypedFunc
def describe(value: object) -> str:
    raise NotImplementedError


@describe.register()
def describe_integer(value: int) -> str:
    return f"integer: {value}"


@describe.register()
def describe_string(value: str) -> str:
    return f"string: {value}"


@describe.register(
    lambda value: value > 0,
    priority=10,
)
def describe_positive_integer(value: int) -> str:
    return f"positive integer: {value}"


print(describe(-2))       # integer: -2
print(describe(42))       # positive integer: 42
print(describe("hello"))  # string: hello
```

Additional validators can be passed to `TypedFunc.register()`; they must all
return `True` for the implementation to be selected.

The runtime type checker supports ordinary classes, unions, `Literal`, and
element checks for annotated lists, sets, dictionaries, and tuples. Runtime
checking cannot enforce every constraint expressible by Python's typing
system.

## CompareDecorator

Use `CompareDecorator` to extract values from call arguments and register
implementations for comparison ranges.

```python
from overfunc import CompareDecorator


@CompareDecorator(amount=lambda amount: amount)
def price_band(amount: float) -> str:
    raise NotImplementedError


@price_band.register().lt(amount=0)
def credit(amount: float) -> str:
    return "credit"


@price_band.register().ge(amount=0).lt(amount=100)
def regular(amount: float) -> str:
    return "regular"


@price_band.register().ge(amount=100)
def bulk(amount: float) -> str:
    return "bulk"


print(price_band(-5))   # "credit"
print(price_band(25))   # "regular"
print(price_band(125))  # "bulk"
```

The keyword in each comparison (here, `amount`) refers to a configured
getter. Getters can also be created from argument attributes with
`CompareDecorator().with_attr("value")`.

## VersionedDecorator

Use `VersionedDecorator` to select an implementation for a version interval.
The upper bound is exclusive.

```python
from overfunc import VersionedDecorator


@VersionedDecorator(version=lambda version: version)
def decode(version: tuple[int, int]) -> str:
    raise NotImplementedError


@decode.register().for_version(initial=(1, 0), final=(2, 0))
def decode_v1(version: tuple[int, int]) -> str:
    return "v1 format"


@decode.register().for_version(initial=(2, 0))
def decode_v2(version: tuple[int, int]) -> str:
    return "v2 format"


print(decode((1, 5)))  # "v1 format"
print(decode((2, 1)))  # "v2 format"
```

Version decorators can also use named argument attributes and tags to combine
version and other comparison rules.
