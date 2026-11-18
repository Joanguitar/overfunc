# overfunc

`overfunc` dispatches a call to one of several registered implementations.
Use `MultiFunc` with explicit validators, or `TypedFunc` to select an
implementation using its argument annotations.

## Installation

```bash
pip install overfunc
```

## MultiFunc

Create a dispatcher with a representative function, then register
implementations with validators. Validators receive the same arguments as the
call and return `True` when their implementation should be selected.

```python
from overfunc.multifunc import MultiFunc


def describe(value: object) -> str:
    raise NotImplementedError


describe_value = MultiFunc(describe)


@describe_value.register(lambda value: isinstance(value, int))
def describe_integer(value: object) -> str:
    return f"integer: {value}"


@describe_value.register(lambda value: isinstance(value, str))
def describe_string(value: object) -> str:
    return f"string: {value}"


print(describe_value(42))       # integer: 42
print(describe_value("hello"))  # string: hello
```

When multiple validators match, implementations registered with a priority
are checked first, from highest to lowest. Implementations without a priority
are checked afterward in registration order.

```python
@describe_value.register(
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
from overfunc.typedfunc import TypedFunc


def convert(value: object) -> str:
    raise NotImplementedError


convert_value = TypedFunc(convert)


@convert_value.register()
def convert_integer(value: int) -> str:
    return str(value)


@convert_value.register()
def convert_string(value: str) -> str:
    return value


print(convert_value(42))       # "42"
print(convert_value("hello"))  # "hello"
```

Additional validators can be passed to `TypedFunc.register()`; they must all
return `True` for the implementation to be selected.

The runtime type checker supports ordinary classes, unions, `Literal`, and
element checks for annotated lists, sets, dictionaries, and tuples. Runtime
checking cannot enforce every constraint expressible by Python's typing
system.
