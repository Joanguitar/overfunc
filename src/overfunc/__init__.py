"""Function overloading and dispatch utilities."""

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .comparefunc import CompareDecorator, CompareFunc
    from .multifunc import MultiFunc
    from .typedfunc import TypedFunc
    from .versionfunc import VersionedDecorator, VersionedFunc

__all__ = [
    "MultiFunc",
    "TypedFunc",
    "CompareFunc",
    "VersionedFunc",
    "CompareDecorator",
    "VersionedDecorator",
]

_LAZY_IMPORTS = {
    "MultiFunc": (".multifunc", "MultiFunc"),
    "TypedFunc": (".typedfunc", "TypedFunc"),
    "CompareFunc": (".comparefunc", "CompareFunc"),
    "VersionedFunc": (".versionfunc", "VersionedFunc"),
    "CompareDecorator": (".comparefunc", "CompareDecorator"),
    "VersionedDecorator": (".versionfunc", "VersionedDecorator"),
}


def __getattr__(name: str) -> Any:
    try:
        module_name, attribute_name = _LAZY_IMPORTS[name]
    except KeyError:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from None

    module = import_module(module_name, __name__)
    value = getattr(module, attribute_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
